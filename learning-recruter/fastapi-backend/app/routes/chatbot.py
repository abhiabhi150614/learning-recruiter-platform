import re
import requests
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.schemas.chatbot import ChatMessage, ChatResponse
from app.core.gemini_ai import chatbot
from app.core.security import decode_token
from app.database.db import get_db
from app.core.learning_path_service import LearningPathService
from app.models.quiz import QuizSubmission
from app.models.learning_plan import LearningPlan
from app.models.user import User
from app.core.google_services import get_day_notes, list_drive_files, update_day_notes
from app.core.youtube_services import search_youtube_videos, get_user_playlists, create_playlist, add_video_to_playlist, get_video_summary, get_playlist_summary, extract_video_id_from_url
from app.core.call_bot import call_bot
from app.core.config import settings
import logging

# Set up logging
logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer()
router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(message: ChatMessage, credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(get_db)):
    """Send message to AI chatbot and get response"""
    try:
        # Verify token and get user ID
        token = credentials.credentials
        user_id = decode_token(token)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_id_int = int(user_id)
        
        # Build comprehensive learning context
        context_snippets = []
        try:
            # Get user and onboarding information
            user = db.query(User).filter(User.id == user_id_int).first()
            if user:
                user_name = user.google_name or "Abhishek"
                context_snippets.append(f"USER: {user_name}")
                context_snippets.append(f"CURRENT_POSITION: Day {user.current_day}, Month {user.current_month_index}")
                
                # Add onboarding data
                from app.models.onboarding import Onboarding
                onboarding = db.query(Onboarding).filter(Onboarding.user_id == user_id_int).first()
                if onboarding:
                    context_snippets.append(f"USER_GOALS: {onboarding.career_goals}")
                    context_snippets.append(f"CURRENT_SKILLS: {onboarding.current_skills}")
                    context_snippets.append(f"TIME_COMMITMENT: {onboarding.time_commitment}")
                    context_snippets.append(f"GRADE_LEVEL: {onboarding.grade}")
            
            # Get comprehensive learning plan information
            plan = db.query(LearningPlan).filter(LearningPlan.user_id == user_id_int).first()
            if plan and plan.plan and isinstance(plan.plan, dict) and "months" in plan.plan:
                context_snippets.append(f"LEARNING_PLAN: {plan.title}")
                context_snippets.append(f"PLAN_CREATED: {plan.created_at}")
                
                months = plan.plan.get("months", [])
                current_month_index = user.current_month_index if user else 1
                current_day = user.current_day if user else 1
                
                # Current month details
                current_month = None
                for month in months:
                    if month.get("index") == current_month_index:
                        current_month = month
                        break
                
                if current_month:
                    context_snippets.append(f"CURRENT_MONTH: {current_month.get('title')}")
                    context_snippets.append(f"MONTH_STATUS: {current_month.get('status')}")
                    
                    days = current_month.get("days", [])
                    if days and 0 < current_day <= len(days):
                        today = days[current_day - 1]
                        context_snippets.append(f"TODAY_TOPIC: {today.get('concept')}")
                        context_snippets.append(f"TODAY_DESCRIPTION: {today.get('description', '')[:200]}")
                        context_snippets.append(f"TODAY_COMPLETED: {today.get('completed', False)}")
                        
                        # Learning objectives
                        objectives = today.get('learning_objectives', [])
                        if objectives:
                            context_snippets.append(f"TODAY_OBJECTIVES: {'; '.join(objectives[:3])}")
                        
                        # Resources available
                        resources = today.get('resources', [])
                        if resources:
                            context_snippets.append(f"TODAY_RESOURCES: {len(resources)} items available")
                        
                        # Completed days in current month
                        completed_days = [i+1 for i, day in enumerate(days) if day.get('completed', False)]
                        context_snippets.append(f"MONTH_COMPLETED_DAYS: {completed_days}")
                        context_snippets.append(f"MONTH_PROGRESS: {len(completed_days)}/{len(days)} days")
            
            # Comprehensive quiz performance
            all_quizzes = db.query(QuizSubmission).filter(
                QuizSubmission.user_id == user_id_int
            ).order_by(QuizSubmission.created_at.desc()).limit(10).all()
            
            if all_quizzes:
                passed_count = sum(1 for q in all_quizzes if q.passed)
                avg_score = sum(q.score for q in all_quizzes) / len(all_quizzes)
                context_snippets.append(f"QUIZ_PERFORMANCE: {passed_count}/{len(all_quizzes)} passed, Average: {avg_score:.0f}%")
                
                latest = all_quizzes[0]
                status = "PASSED" if latest.passed else "FAILED"
                context_snippets.append(f"LATEST_QUIZ: Month {latest.month_index}, Day {latest.day}, Score: {latest.score}% ({status})")
                
                # Recent quiz history
                recent_history = []
                for q in all_quizzes[:5]:
                    status = "PASS" if q.passed else "FAIL"
                    recent_history.append(f"M{q.month_index}D{q.day}:{q.score}%({status})")
                context_snippets.append(f"QUIZ_HISTORY: {', '.join(recent_history)}")
            
            # Overall progress summary
            if plan:
                try:
                    summary = LearningPathService.get_user_progress_summary(db, user_id_int, plan.id)
                    context_snippets.append(f"OVERALL_PROGRESS: {summary.get('overall_progress_percentage', 0)}% complete")
                    context_snippets.append(f"DAYS_COMPLETED: {summary.get('total_days_completed', 0)}/{summary.get('total_days', 0)}")
                    context_snippets.append(f"DAYS_STARTED: {summary.get('total_days_started', 0)}")
                except:
                    context_snippets.append("PROGRESS_DATA: Unavailable")
                
            # Note: Notes functionality now handled by AI tools automatically
            
            # Note: Call functionality now handled by AI tools automatically
            
            # LinkedIn posting functionality
            linkedin_post_keywords = ["create post", "linkedin post", "post on linkedin", "share on linkedin", "make a post", "post this", "now post this"]
            if any(keyword in message.message.lower() for keyword in linkedin_post_keywords):
                # Extract topic from message - improved patterns
                topic_match = re.search(r'(?:post|share|create)\s+(?:about|on|regarding|this)?\s*(.+?)(?:\.|$|in linkedin)', message.message.lower())
                if not topic_match:
                    # Try alternative patterns
                    topic_match = re.search(r'(?:about|on)\s+(.+?)(?:\s+in|\s+on|$)', message.message.lower())
                
                if topic_match:
                    topic = topic_match.group(1).strip()
                    if topic in ['this', 'it', 'that']:  # Handle "post this" cases
                        topic = "Python fundamentals"  # Default from context
                    
                    context_snippets.append(f"LinkedInPostRequest: User wants to create a LinkedIn post about '{topic}'")
                    
                    # Generate content using AI with user context
                    user_context_str = " ".join(context_snippets)
                    generated_content = generate_linkedin_content(topic, user_context_str)
                    
                    context_snippets.append(f"GeneratedContent: {generated_content[:100]}...")
                    
                    # Create the LinkedIn post
                    try:
                        from app.core.composio_service import composio_auth
                        post_result = composio_auth.create_linkedin_post(user.email, generated_content)
                        
                        if post_result.get('success'):
                            context_snippets.append(f"LinkedInPostCreated: Successfully posted to LinkedIn about '{topic}'")
                            context_snippets.append(f"PostContent: {generated_content}")
                            context_snippets.append("InstructAI: Confirm the LinkedIn post was successfully published and show the user the exact content that was posted.")
                        else:
                            error_msg = post_result.get('error', 'Unknown error')
                            context_snippets.append(f"LinkedInPostError: Failed to create post - {error_msg}")
                            context_snippets.append("InstructAI: The LinkedIn post creation failed. Check if LinkedIn is properly connected in social connections.")
                    
                    except Exception as e:
                        context_snippets.append(f"LinkedInPostError: Exception occurred - {str(e)}")
                        context_snippets.append("InstructAI: Technical error creating LinkedIn post. Check social connections and try again.")
                else:
                    # Handle "post this" without clear topic
                    if "post this" in message.message.lower() or "now post this" in message.message.lower():
                        topic = "Python fundamentals"  # Use recent context
                        context_snippets.append(f"LinkedInPostRequest: User wants to post previous content about '{topic}'")
                        
                        user_context_str = " ".join(context_snippets)
                        generated_content = generate_linkedin_content(topic, user_context_str)
                        
                        try:
                            from app.core.composio_service import composio_auth
                            post_result = composio_auth.create_linkedin_post(user.email, generated_content)
                            
                            if post_result.get('success'):
                                context_snippets.append(f"LinkedInPostCreated: Successfully posted to LinkedIn")
                                context_snippets.append(f"PostContent: {generated_content}")
                                context_snippets.append("InstructAI: Your LinkedIn post has been published successfully! Here's what was posted.")
                            else:
                                error_msg = post_result.get('error', 'Unknown error')
                                context_snippets.append(f"LinkedInPostError: {error_msg}")
                                context_snippets.append("InstructAI: LinkedIn posting failed. Please check your LinkedIn connection.")
                        except Exception as e:
                            context_snippets.append(f"LinkedInPostError: {str(e)}")
                            context_snippets.append("InstructAI: Technical error. Please try again or check social connections.")
                    else:
                        context_snippets.append("LinkedInPostRequest: User wants to create a LinkedIn post but no specific topic was identified")
                        context_snippets.append("InstructAI: What topic would you like to post about on LinkedIn?")
            
            # YouTube-related functionality
            youtube_keywords = ["youtube", "video", "videos", "playlist", "find video", "search video", "link", "give me", "add to", "summary of", "summarize"]
            if any(keyword in message.message.lower() for keyword in youtube_keywords):
                # Store video search results for later use
                searched_videos = None
                
                # Check for video search request
                video_search_match = re.search(r'(?:find|give|show|get|search for|look for)\s+(?:me\s+)?(?:the\s+)?(?:video|videos|youtube|link)\s+(?:for|about|on|related to|on topic)\s+(.+?)(?:\.|$)', message.message.lower())
                
                # Check for specific learning topic request
                learning_topic_match = None
                if not video_search_match and plan and plan.plan and isinstance(plan.plan, dict) and "months" in plan.plan:
                    months = plan.plan.get("months", [])
                    current_month_index = user.current_month_index if user else 1
                    current_day = user.current_day if user else 1
                    
                    if 1 <= current_month_index <= len(months):
                        current_month = months[current_month_index - 1]
                        days = current_month.get("days", [])
                        if 0 < current_day <= len(days):
                            current_day_data = days[current_day - 1]
                            concept = current_day_data.get('concept')
                            if concept and ("today" in message.message.lower() or "current" in message.message.lower() or "learning" in message.message.lower()):
                                # Extract key terms from the concept for better search results
                                concept_keywords = re.sub(r'[\(\):]', '', concept)  # Remove parentheses and colons
                                concept_parts = concept_keywords.split(':')
                                main_concept = concept_parts[0] if concept_parts else concept_keywords
                                
                                # Create a more focused search query
                                learning_topic_match = f"tutorial {main_concept.strip()}"
                                context_snippets.append(f"YouTubeSearchRequest: User wants videos for today's learning topic: '{concept}'")
                                context_snippets.append(f"SearchQuery: Using optimized search query: '{learning_topic_match}'")
                
                search_query = ""
                if video_search_match:
                    search_query = video_search_match.group(1).strip()
                    context_snippets.append(f"YouTubeSearchRequest: User wants to find videos about '{search_query}'")
                elif learning_topic_match:
                    search_query = learning_topic_match
                elif "today" in message.message.lower() and "learning" in message.message.lower():
                    # If user just asks for today's learning without specific topic match
                    if plan and plan.plan and isinstance(plan.plan, dict) and "months" in plan.plan:
                        months = plan.plan.get("months", [])
                        current_month_index = user.current_month_index if user else 1
                        current_day = user.current_day if user else 1
                        
                        if 1 <= current_month_index <= len(months):
                            current_month = months[current_month_index - 1]
                            days = current_month.get("days", [])
                            if 0 < current_day <= len(days):
                                current_day_data = days[current_day - 1]
                                concept = current_day_data.get('concept')
                                if concept:
                                    # Create a more focused search query
                                    concept_keywords = re.sub(r'[\(\):]', '', concept)  # Remove parentheses and colons
                                    search_query = f"tutorial {concept_keywords.strip()}"
                                    context_snippets.append(f"YouTubeSearchRequest: User wants videos for today's learning topic: '{concept}'")
                                    context_snippets.append(f"SearchQuery: Using optimized search query: '{search_query}'")
                
                if search_query:
                    # Search for videos
                    searched_videos = search_youtube_videos(user_id_int, search_query, 5)  # Limit to 5 videos
                    if searched_videos:
                        context_snippets.append(f"YouTubeSearchResults: Found {len(searched_videos)} videos matching '{search_query}'")
                        
                        # Add detailed information about each video for better responses
                        for i, video in enumerate(searched_videos[:3]):  # Include top 3 videos in context
                            video_title = video.get('title', '')
                            video_url = video.get('url', '')
                            video_id = video.get('id', '')
                            video_duration_mins = video.get('duration_seconds', 0) // 60
                            video_duration_secs = video.get('duration_seconds', 0) % 60
                            video_channel = video.get('channel', '')
                            
                            # Format video information with complete details
                            context_snippets.append(f"Video{i+1}Title: {video_title}")
                            context_snippets.append(f"Video{i+1}URL: {video_url}")
                            context_snippets.append(f"Video{i+1}ID: {video_id}")
                            context_snippets.append(f"Video{i+1}Duration: {video_duration_mins}m{video_duration_secs}s")
                            context_snippets.append(f"Video{i+1}Channel: {video_channel}")
                            context_snippets.append(f"Video{i+1}URLMarkdown: [Watch: {video_title}]({video_url})")
                            
                            # Add a direct instruction for the AI to use this URL
                            if i == 0:  # For the first (most relevant) video
                                context_snippets.append(f"RecommendedVideoURL: {video_url}")
                                context_snippets.append(f"RecommendedVideoTitle: {video_title}")
                                context_snippets.append(f"RecommendedVideoID: {video_id}")
                                context_snippets.append(f"RecommendedVideoURLMarkdown: [Watch: {video_title}]({video_url})")
                                context_snippets.append(f"InstructAI: Please provide the user with the clickable link to the recommended video using the RecommendedVideoURLMarkdown format.")
                    else:
                        context_snippets.append(f"YouTubeSearchResults: No videos found matching '{search_query}'")
                
                # Check for playlist creation request
                create_playlist_match = re.search(r'(?:create|make)\s+(?:a|new)?\s*playlist\s+(?:called|named|with name)?\s*["\'](.+?)["\']', message.message.lower())
                if create_playlist_match:
                    playlist_name = create_playlist_match.group(1).strip()
                    context_snippets.append(f"CreatePlaylistRequest: User wants to create a playlist named '{playlist_name}'")
                    
                    # Create the playlist
                    try:
                        print(f"Creating playlist '{playlist_name}' for user {user_id_int}")
                        
                        # First check if user has Google authentication
                        user = db.query(User).filter(User.id == user_id_int).first()
                        if not user or not user.google_id or not user.google_access_token:
                            context_snippets.append(
                                f"PlaylistCreationError: User does not have proper Google authentication set up"
                            )
                            context_snippets.append(
                                "InstructAI: Please inform the user that they need to connect their Google account first. They should go to their profile settings and link their Google account with YouTube permissions."
                            )
                            logger.error(f"User {user_id_int} does not have Google authentication set up")
                        else:
                            print(f"User has Google authentication: {user.google_id}")
                            new_playlist = create_playlist(
                                user_id_int,
                                playlist_name,
                                f"Learning playlist for {playlist_name} created by EduAI"
                            )

                            print(f"Playlist creation result: {new_playlist}")
                            print(f"Type of result: {type(new_playlist)}")
                            print(f"Has 'id': {new_playlist.get('id') if new_playlist else 'None'}")
                            print(f"Has 'error': {'error' in new_playlist if isinstance(new_playlist, dict) else 'Not a dict'}")

                            if new_playlist and new_playlist.get('id') and 'error' not in new_playlist:
                                print(f"✅ PLAYLIST CREATED SUCCESSFULLY: {new_playlist}")
                                context_snippets.append(
                                    f"PlaylistCreated: Yes, created playlist '{playlist_name}' with ID {new_playlist.get('id')}"
                                )
                                context_snippets.append(f"PlaylistURL: {new_playlist.get('url')}")
                                context_snippets.append(
                                    f"PlaylistURLMarkdown: [Click here to access your '{playlist_name}' playlist]({new_playlist.get('url')})"
                                )
                                context_snippets.append(
                                    "InstructAI: Please confirm the playlist was created successfully and provide the user with the clickable link to their playlist using the PlaylistURLMarkdown format. Also mention the playlist name."
                                )

                                # Try to add a video to the newly created playlist
                                video_id = None
                                
                                # First check if there's a video URL in the message
                                video_url_match = re.search(r'(https?://(?:www\.)?youtube\.com/watch\?v=([\w-]+)(?:[&\w=]*))', message.message)
                                if video_url_match:
                                    video_url = video_url_match.group(1)
                                    extracted_video_id = extract_video_id_from_url(video_url)
                                    if extracted_video_id:
                                        video_id = extracted_video_id
                                        print(f"Found video URL in message: {video_url}, extracted ID: {video_id}")
                                        context_snippets.append(f"VideoToAdd: Found video ID {video_id} from message URL")
                                    else:
                                        print(f"Could not extract video ID from URL: {video_url}")
                                        context_snippets.append(f"VideoToAdd: Could not extract video ID from URL {video_url}")
                                
                                # If no URL in message, check if we have recent search results
                                elif searched_videos and len(searched_videos) > 0:
                                    first_video = searched_videos[0]
                                    video_id = first_video.get('id')
                                    print(f"Using first search result video ID: {video_id}")
                                    context_snippets.append(f"VideoToAdd: Using first search result video ID {video_id}")
                                
                                # If still no video ID, check if the message mentions a specific video title
                                else:
                                    video_title_match = re.search(r'(?:video|add)\s+["\'](.+?)["\']', message.message.lower())
                                    if video_title_match:
                                        video_title = video_title_match.group(1)
                                        print(f"Searching for video with title: {video_title}")
                                        # Search for this specific video
                                        specific_videos = search_youtube_videos(user_id_int, video_title, 1)
                                        if specific_videos and len(specific_videos) > 0:
                                            video_id = specific_videos[0].get('id')
                                            print(f"Found video ID {video_id} for title '{video_title}'")
                                            context_snippets.append(f"VideoToAdd: Found video ID {video_id} for title '{video_title}'")
                                
                                if video_id:
                                    print(f"Attempting to add video {video_id} to new playlist '{playlist_name}'")
                                    result = add_video_to_playlist(user_id_int, new_playlist.get("id"), video_id)
                                    print(f"Auto-video addition result: {result}")
                                    
                                    if result is True:
                                        context_snippets.append(
                                            f"VideoAdded: Yes, successfully added video {video_id} to new playlist '{playlist_name}'"
                                        )
                                        video_url = f"https://www.youtube.com/watch?v={video_id}"
                                        context_snippets.append(f"AddedVideoURL: {video_url}")
                                        context_snippets.append(f"AddedVideoURLMarkdown: [Watch the video you added]({video_url})")
                                        context_snippets.append(f"InstructAI: Please confirm the video was successfully added to the new playlist and provide the user with the clickable link to the video using the AddedVideoURLMarkdown format. Also mention which playlist it was added to.")
                                    elif isinstance(result, dict) and 'error' in result:
                                        error_message = result['error']
                                        context_snippets.append(
                                            f"VideoAdded: No, failed to add video {video_id} to playlist '{playlist_name}'. Error: {error_message}"
                                        )
                                        context_snippets.append(f"InstructAI: Please inform the user that there was an error adding the video to the playlist: {error_message}. Suggest they check their YouTube permissions or try again.")
                                    else:
                                        context_snippets.append(
                                            f"VideoAdded: No, failed to add video {video_id} to playlist '{playlist_name}'"
                                        )
                                else:
                                    print(f"No video found to add to new playlist '{playlist_name}'")
                                    context_snippets.append(f"VideoToAdd: No video URL found in message and no recent search results available")
                            else:
                                error_message = new_playlist.get('error', 'Unknown error') if isinstance(new_playlist, dict) else str(new_playlist)
                                print(f"❌ PLAYLIST CREATION FAILED: {error_message}")
                                print(f"❌ Full response: {new_playlist}")
                                context_snippets.append(
                                    f"PlaylistCreationError: Failed to create playlist '{playlist_name}'. Error: {error_message}"
                                )
                                context_snippets.append(
                                    f"InstructAI: Please inform the user that playlist creation failed: {error_message}. Suggest they check their Google authentication and YouTube permissions."
                                )
                                logger.error(f"Failed to create playlist '{playlist_name}' for user {user_id}. Error: {error_message}")

                    except Exception as e:
                        context_snippets.append(f"PlaylistCreationError: Exception occurred: {str(e)}")
                        context_snippets.append(
                            "InstructAI: Please inform the user that there was a technical error creating the playlist. Suggest they try again or contact support if the issue persists."
                        )
                        logger.error(f"Exception creating playlist '{playlist_name}' for user {user_id}: {str(e)}")
                        import traceback
                        logger.error(traceback.format_exc())
                
                # Check for add to playlist request (multiple flexible patterns)
                playlist_match = None
                
                # Pattern 1: "add video to playlist name"
                playlist_match = re.search(r'add\s+(?:this|that|the)?\s*(?:video)?\s*(?:to|into)\s+(?:my|the)?\s*playlist\s*(?:called|named)?\s*["\']?([^"\']+?)["\']?(?:\s|$)', message.message.lower())
                
                # Pattern 2: "add to playlist name"
                if not playlist_match:
                    playlist_match = re.search(r'add\s+to\s+(?:my|the)?\s*playlist\s*(?:called|named)?\s*["\']?([^"\']+?)["\']?(?:\s|$)', message.message.lower())
                
                # Pattern 3: "add to name playlist"
                if not playlist_match:
                    playlist_match = re.search(r'add\s+(?:this|that|the)?\s*(?:video)?\s*(?:to|into)\s+["\']?([^"\']+?)["\']?\s*playlist', message.message.lower())
                
                # Pattern 4: "add video to name" (most flexible)
                if not playlist_match:
                    playlist_match = re.search(r'add\s+(?:this|that|the)?\s*(?:video)?\s*(?:to|into)\s+["\']?([^"\']+?)["\']?(?:\s|$)', message.message.lower())
                
                # Pattern 5: "add to name" (most basic)
                if not playlist_match:
                    playlist_match = re.search(r'add\s+to\s+["\']?([^"\']+?)["\']?(?:\s|$)', message.message.lower())
                
                if playlist_match:
                    playlist_name = playlist_match.group(1).strip()
                    print(f"🎯 DETECTED: Add to playlist request for '{playlist_name}'")
                    print(f"🎯 Original message: '{message.message}'")
                    print(f"🎯 Pattern matched: {playlist_match.group(0)}")
                    context_snippets.append(f"PlaylistRequest: User wants to add a video to playlist '{playlist_name}'")
                    
                    # Get user's playlists
                    playlists = get_user_playlists(user_id_int)
                    print(f"Found {len(playlists)} playlists for user {user_id_int}")
                    
                    # Check if the requested playlist exists
                    playlist_exists = False
                    playlist_id = None
                    playlist_url = None
                    for playlist in playlists:
                        playlist_title = playlist.get('title', '').lower().strip()
                        requested_name = playlist_name.lower().strip()
                        print(f"Checking playlist: '{playlist.get('title', '')}' against '{playlist_name}'")
                        print(f"  Normalized: '{playlist_title}' vs '{requested_name}'")
                        
                        if playlist_title == requested_name:
                            playlist_exists = True
                            playlist_id = playlist.get('id')
                            playlist_url = playlist.get('url')
                            print(f"✅ Found playlist: {playlist_id}")
                            break
                    
                    if playlist_exists:
                        print(f"🎯 SUCCESS: Found existing playlist '{playlist_name}' with ID {playlist_id}")
                        context_snippets.append(f"PlaylistFound: Yes, found playlist '{playlist_name}' with ID {playlist_id}")
                        context_snippets.append(f"PlaylistURL: {playlist_url}")
                        context_snippets.append(f"PlaylistURLMarkdown: [Access your '{playlist_name}' playlist]({playlist_url})")
                        
                        # Check if there's a video URL in the message to add
                        # Handle different YouTube URL formats
                        video_url_match = re.search(r'(https?://(?:www\.)?youtube\.com/watch\?v=([\w-]+)(?:[&\w=]*))', message.message)
                        video_id = None
                        if video_url_match:
                            video_url = video_url_match.group(1)
                            # Use the improved video ID extraction
                            extracted_video_id = extract_video_id_from_url(video_url)
                            if extracted_video_id:
                                video_id = extracted_video_id
                                context_snippets.append(f"VideoToAdd: Found video ID {video_id} to add to playlist")
                                context_snippets.append(f"VideoURL: {video_url}")
                            else:
                                context_snippets.append(f"VideoToAdd: Could not extract video ID from URL {video_url}")
                        
                        # If no URL in message, check if we have recent search results
                        elif searched_videos and len(searched_videos) > 0:
                            first_video = searched_videos[0]
                            video_id = first_video.get('id')
                            context_snippets.append(f"VideoToAdd: Using first search result video ID {video_id} to add to playlist")
                        
                        # If still no video ID, check if the message mentions a specific video
                        else:
                            # Try to extract video title from message
                            video_title_match = re.search(r'(?:video|add)\s+["\'](.+?)["\']', message.message.lower())
                            if video_title_match:
                                video_title = video_title_match.group(1)
                                # Search for this specific video
                                specific_videos = search_youtube_videos(user_id_int, video_title, 1)
                                if specific_videos and len(specific_videos) > 0:
                                    video_id = specific_videos[0].get('id')
                                    context_snippets.append(f"VideoToAdd: Found video ID {video_id} for title '{video_title}'")
                        
                        if video_id:
                            # Add video to playlist
                            try:
                                print(f"🎯 ATTEMPTING: Add video {video_id} to existing playlist '{playlist_name}' (ID: {playlist_id})")
                                result = add_video_to_playlist(user_id_int, playlist_id, video_id)
                                print(f"🎯 VIDEO ADDITION RESULT: {result}")
                                
                                if result is True:
                                    context_snippets.append(f"VideoAdded: Yes, successfully added video {video_id} to playlist '{playlist_name}'")
                                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                                    context_snippets.append(f"AddedVideoURL: {video_url}")
                                    context_snippets.append(f"AddedVideoURLMarkdown: [Watch the video you added]({video_url})")
                                    context_snippets.append(f"InstructAI: Please confirm the video was successfully added to the playlist and provide the user with the clickable link to the video using the AddedVideoURLMarkdown format. Also mention which playlist it was added to.")
                                elif isinstance(result, dict) and 'error' in result:
                                    error_message = result['error']
                                    context_snippets.append(f"VideoAdded: No, failed to add video {video_id} to playlist '{playlist_name}'. Error: {error_message}")
                                    context_snippets.append(f"InstructAI: Please inform the user that there was an error adding the video to the playlist: {error_message}. Suggest they check their YouTube permissions or try again.")
                                    logger.error(f"Failed to add video {video_id} to playlist '{playlist_name}' for user {user_id_int}. Error: {error_message}")
                                else:
                                    context_snippets.append(f"VideoAdded: No, failed to add video {video_id} to playlist '{playlist_name}'")
                                    context_snippets.append(f"InstructAI: Please inform the user that there was an error adding the video to the playlist and suggest they check their YouTube permissions or try again.")
                            except Exception as e:
                                context_snippets.append(f"VideoAddError: {str(e)}")
                                logger.error(f"Error adding video to playlist: {str(e)}")
                        else:
                            context_snippets.append("VideoToAdd: No video URL found in message and no recent search results available")
                            context_snippets.append("InstructAI: Please inform the user that no video was found to add to the playlist. Ask them to provide a YouTube URL or search for a video first.")
                    else:
                        print(f"❌ Playlist '{playlist_name}' not found. Available playlists:")
                        for p in playlists:
                            print(f"  - '{p.get('title', '')}' (ID: {p.get('id', '')})")
                        context_snippets.append(f"PlaylistFound: No, could not find playlist '{playlist_name}'. Available playlists: {[p.get('title', '') for p in playlists]}")
                        
                        # Try to find a video to add to the existing playlist
                        video_id = None
                        
                        # First check if there's a video URL in the message
                        video_url_match = re.search(r'(https?://(?:www\.)?youtube\.com/watch\?v=([\w-]+)(?:[&\w=]*))', message.message)
                        if video_url_match:
                            video_url = video_url_match.group(1)
                            extracted_video_id = extract_video_id_from_url(video_url)
                            if extracted_video_id:
                                video_id = extracted_video_id
                                print(f"Found video URL in message: {video_url}, extracted ID: {video_id}")
                                context_snippets.append(f"VideoToAdd: Found video ID {video_id} from message URL")
                            else:
                                print(f"Could not extract video ID from URL: {video_url}")
                                context_snippets.append(f"VideoToAdd: Could not extract video ID from URL {video_url}")
                        elif searched_videos and len(searched_videos) > 0:
                            first_video = searched_videos[0]
                            video_id = first_video.get('id')
                            print(f"Using first search result video ID: {video_id}")
                            context_snippets.append(f"VideoToAdd: Using first search result video ID {video_id}")
                        
                        # Create the playlist automatically
                        try:
                            print(f"Auto-creating playlist '{playlist_name}' for user {user_id_int}")
                            
                            # First check if user has Google authentication
                            user = db.query(User).filter(User.id == user_id_int).first()
                            if not user or not user.google_id or not user.google_access_token:
                                context_snippets.append(
                                    f"PlaylistCreationError: User does not have proper Google authentication set up"
                                )
                                context_snippets.append(
                                    "InstructAI: Please inform the user that they need to connect their Google account first. They should go to their profile settings and link their Google account with YouTube permissions."
                                )
                                logger.error(f"User {user_id_int} does not have Google authentication set up")
                            else:
                                print(f"User has Google authentication: {user.google_id}")
                                new_playlist = create_playlist(user_id_int, playlist_name, f"Learning playlist for {playlist_name} created by EduAI")
                                print(f"Auto-playlist creation result: {new_playlist}")
                                
                                if new_playlist and new_playlist.get('id') and 'error' not in new_playlist:
                                    context_snippets.append(f"PlaylistCreated: Yes, created playlist '{playlist_name}' with ID {new_playlist.get('id')}")
                                    context_snippets.append(f"PlaylistURL: {new_playlist.get('url')}")
                                    context_snippets.append(f"PlaylistURLMarkdown: [Click here to access your '{playlist_name}' playlist]({new_playlist.get('url')})")
                                    context_snippets.append(f"InstructAI: Please provide the user with the clickable link to their playlist using the PlaylistURLMarkdown format.")
                                    
                                    # Now try to add the video to the newly created playlist
                                    video_url_match = re.search(r'(https?://(?:www\.)?youtube\.com/watch\?v=([\w-]+)(?:[&\w=]*))', message.message)
                                    video_id = None
                                    if video_url_match:
                                        video_url = video_url_match.group(1)
                                        extracted_video_id = extract_video_id_from_url(video_url)
                                        if extracted_video_id:
                                            video_id = extracted_video_id
                                    elif searched_videos and len(searched_videos) > 0:
                                        first_video = searched_videos[0]
                                        video_id = first_video.get('id')
                                    
                                    if video_id:
                                        result = add_video_to_playlist(user_id_int, new_playlist.get('id'), video_id)
                                        print(f"Auto-video addition result (second instance): {result}")
                                        
                                        if result is True:
                                            context_snippets.append(f"VideoAdded: Yes, successfully added video {video_id} to new playlist '{playlist_name}'")
                                            video_url = f"https://www.youtube.com/watch?v={video_id}"
                                            context_snippets.append(f"AddedVideoURL: {video_url}")
                                            context_snippets.append(f"AddedVideoURLMarkdown: [Watch the video you added]({video_url})")
                                            context_snippets.append(f"InstructAI: Please confirm the video was successfully added to the new playlist and provide the user with the clickable link to the video using the AddedVideoURLMarkdown format. Also mention which playlist it was added to.")
                                        elif isinstance(result, dict) and 'error' in result:
                                            error_message = result['error']
                                            context_snippets.append(f"VideoAdded: No, failed to add video {video_id} to playlist '{playlist_name}'. Error: {error_message}")
                                            context_snippets.append(f"InstructAI: Please inform the user that there was an error adding the video to the playlist: {error_message}. Suggest they check their YouTube permissions or try again.")
                                        else:
                                            context_snippets.append(f"VideoAdded: No, failed to add video {video_id} to playlist '{playlist_name}'")
                                            context_snippets.append(f"InstructAI: Please inform the user that there was an error adding the video to the playlist and suggest they check their YouTube permissions or try again.")
                                else:
                                    error_message = new_playlist.get('error', 'Unknown error') if isinstance(new_playlist, dict) else str(new_playlist)
                                    context_snippets.append(f"PlaylistCreated: No, failed to create playlist '{playlist_name}'. Error: {error_message}")
                                    context_snippets.append(f"InstructAI: Please inform the user that playlist creation failed: {error_message}. Suggest they check their Google authentication and YouTube permissions.")
                                    logger.error(f"Failed to create playlist '{playlist_name}' for user {user_id}. Error: {error_message}")
                        except Exception as e:
                            context_snippets.append(f"PlaylistCreationError: Exception occurred: {str(e)}")
                            context_snippets.append(f"InstructAI: Please inform the user that there was a technical error creating the playlist. Suggest they try again or contact support if the issue persists.")
                            logger.error(f"Exception during playlist creation for user {user_id}: {str(e)}")
                            import traceback
                            logger.error(traceback.format_exc())
                
                # Check for video summary request
                video_summary_match = re.search(r'(?:summarize|summary)\s+(?:of|for)?\s*(?:the)?\s*(?:video)?\s*(?:https?://(?:www\.)?youtube\.com/watch\?v=([\w-]+)(?:[&\w=]*))', message.message.lower())
                if not video_summary_match:
                    # Alternative pattern for video summary
                    video_summary_match = re.search(r'(?:summarize|summary)\s+(?:of|for)?\s*(?:the)?\s*(?:video)?\s*(?:with id)?\s*([\w-]{11})', message.message.lower())
                
                if video_summary_match:
                    video_id = video_summary_match.group(1)
                    
                    # If it's a URL, extract the video ID
                    if video_id.startswith('http'):
                        extracted_video_id = extract_video_id_from_url(video_id)
                        if extracted_video_id:
                            video_id = extracted_video_id
                        else:
                            context_snippets.append(f"VideoSummaryError: Could not extract video ID from URL {video_id}")
                            video_id = None
                    
                    if video_id:
                        context_snippets.append(f"VideoSummaryRequest: User wants a summary of video with ID {video_id}")
                        
                        # Get video summary
                        try:
                            summary = get_video_summary(user_id_int, video_id)
                            if summary:
                                context_snippets.append(f"VideoSummary: {summary}")
                            else:
                                context_snippets.append(f"VideoSummary: Could not generate summary for video with ID {video_id}")
                        except Exception as e:
                            context_snippets.append(f"VideoSummaryError: {str(e)}")
                            logger.error(f"Error generating video summary: {str(e)}")
                    else:
                        context_snippets.append(f"VideoSummaryError: No valid video ID found")
                
                # Check for playlist summary request
                playlist_summary_match = re.search(r'(?:summarize|summary)\s+(?:of|for)?\s*(?:the)?\s*(?:playlist)?\s*(?:https?://(?:www\.)?youtube\.com/playlist\?list=([\w-]+))', message.message.lower())
                if not playlist_summary_match:
                    # Alternative pattern for playlist summary
                    playlist_summary_match = re.search(r'(?:summarize|summary)\s+(?:of|for)?\s*(?:the)?\s*(?:playlist)?\s*(?:with id)?\s*([\w-]+)', message.message.lower())
                
                if playlist_summary_match:
                    playlist_id = playlist_summary_match.group(1)
                    context_snippets.append(f"PlaylistSummaryRequest: User wants a summary of playlist with ID {playlist_id}")
                    
                    # Get playlist summary
                    try:
                        summary = get_playlist_summary(user_id_int, playlist_id)
                        if summary:
                            context_snippets.append(f"PlaylistSummary: Playlist '{summary.get('title')}' has {summary.get('video_count')} videos with total duration {summary.get('total_duration')}")
                            # Add more detailed summary information
                            if 'videos' in summary:
                                for i, video in enumerate(summary['videos'][:3]):
                                    context_snippets.append(f"PlaylistVideo{i+1}: {video.get('title')} ({video.get('duration')})")
                        else:
                            context_snippets.append(f"PlaylistSummary: Could not generate summary for playlist with ID {playlist_id}")
                    except Exception as e:
                        context_snippets.append(f"PlaylistSummaryError: {str(e)}")
                        logger.error(f"Error generating playlist summary: {str(e)}")
        except Exception as e:
            logger.error(f"Context build error: {e}")

        # Create enriched message with comprehensive context
        enriched_message = message.message
        if context_snippets:
            context_header = "[LEARNING_CONTEXT]\n"
            context_header += "You are Abhishek's personal AI learning assistant. Provide specific, actionable study guidance.\n"
            context_header += "\n".join(context_snippets)
            context_header += "\n[/LEARNING_CONTEXT]\n\n"
            context_header += "INSTRUCTIONS:\n"
            context_header += "- Always reference his specific learning plan, current topic, and progress\n"
            context_header += "- Consider his career goals and current skills when giving advice\n"
            context_header += "- Be encouraging but specific about what to study today\n"
            context_header += "- If asked what to study, mention today's topic, objectives, and how it relates to his goals\n"
            context_header += "- Provide actionable next steps based on his current position\n\n"
            enriched_message = context_header + message.message

        # Get AI response with Composio integration
        user = db.query(User).filter(User.id == user_id_int).first()
        user_email = user.email if user else None
        
        if user_email:
            # Use Composio for real-time responses
            response_data = chatbot.get_composio_response(enriched_message, user_email, tools=True, db=db)
        else:
            # Fallback to regular response
            response_data = await chatbot.get_response(enriched_message, user_id_int, tools=True, db=db)
        
        return ChatResponse(
            response=response_data["response"],
            timestamp=response_data["timestamp"],
            message_id=response_data["message_id"]
        )
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process chat message: {str(e)}")

@router.post("/chat/clear")
async def clear_chat_history(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(get_db)):
    """Clear chat session for user"""
    try:
        # Verify token and get user ID
        token = credentials.credentials
        user_id = decode_token(token)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Clear chat session
        success = chatbot.clear_session(int(user_id))
        
        return {"message": "Chat history cleared successfully" if success else "No chat session to clear"}
        
    except Exception as e:
        logger.error(f"Clear chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear chat history: {str(e)}")


@router.get("/notes/{month_index}/{day}")
async def get_notes(month_index: int, day: int, credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(get_db)):
    """Get notes for a specific day from Google Drive"""
    try:
        # Verify token and get user ID
        token = credentials.credentials
        user_id = decode_token(token)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get notes from Google Drive
        notes_data = get_day_notes(int(user_id), month_index, day)
        if not notes_data:
            return {"message": f"No notes found for Month {month_index}, Day {day}", "notes": None, "file_link": None}
        
        return {
            "message": "Notes retrieved successfully", 
            "notes": notes_data.get("content"), 
            "file_link": notes_data.get("link"),
            "file_id": notes_data.get("file_id")
        }
        
    except Exception as e:
        logger.error(f"Get notes error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve notes: {str(e)}")


@router.post("/notes/{month_index}/{day}")
async def update_notes(month_index: int, day: int, content: dict, credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(get_db)):
    """Update notes for a specific day in Google Drive"""
    try:
        # Verify token and get user ID
        token = credentials.credentials
        user_id = decode_token(token)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Validate content
        if "content" not in content:
            raise HTTPException(status_code=400, detail="Content field is required")
        
        # Update notes in Google Drive
        success = update_day_notes(int(user_id), month_index, day, content["content"])
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update notes")
        
        # Get updated notes to return the link
        updated_notes = get_day_notes(int(user_id), month_index, day)
        
        return {
            "message": "Notes updated successfully",
            "file_link": updated_notes.get("link") if updated_notes else None
        }
        
    except Exception as e:
        logger.error(f"Update notes error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update notes: {str(e)}")


@router.get("/youtube/search")
async def search_videos(query: str, max_results: int = 10, credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(get_db)):
    """Search for YouTube videos based on a query"""
    try:
        # Verify token and get user ID
        token = credentials.credentials
        user_id = decode_token(token)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Search for videos
        videos = search_youtube_videos(int(user_id), query, max_results)
        
        return {
            "message": f"Found {len(videos)} videos matching '{query}'",
            "videos": videos
        }
        
    except Exception as e:
        logger.error(f"YouTube search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to search YouTube: {str(e)}")


@router.get("/youtube/playlists")
async def get_playlists(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(get_db)):
    """Get the user's YouTube playlists"""
    try:
        # Verify token and get user ID
        token = credentials.credentials
        user_id = decode_token(token)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get playlists
        playlists = get_user_playlists(int(user_id))
        
        return {
            "message": f"Found {len(playlists)} playlists",
            "playlists": playlists
        }
        
    except Exception as e:
        logger.error(f"YouTube playlists error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get playlists: {str(e)}")


@router.post("/youtube/playlists")
async def create_new_playlist(playlist_data: dict, credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(get_db)):
    """Create a new YouTube playlist"""
    try:
        # Verify token and get user ID
        token = credentials.credentials
        user_id = decode_token(token)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Validate playlist data
        if "title" not in playlist_data:
            raise HTTPException(status_code=400, detail="Title field is required")
        
        # Create playlist
        description = playlist_data.get("description", "")
        playlist = create_playlist(int(user_id), playlist_data["title"], description)
        
        if not playlist:
            raise HTTPException(status_code=500, detail="Failed to create playlist")
        
        return {
            "message": f"Playlist '{playlist_data['title']}' created successfully",
            "playlist": playlist
        }
        
    except Exception as e:
        logger.error(f"YouTube create playlist error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create playlist: {str(e)}")


@router.post("/youtube/playlists/{playlist_id}/videos")
async def add_to_playlist(playlist_id: str, video_data: dict, credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(get_db)):
    """Add a video to a YouTube playlist"""
    try:
        # Verify token and get user ID
        token = credentials.credentials
        user_id = decode_token(token)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Validate video data
        if "video_id" not in video_data:
            raise HTTPException(status_code=400, detail="Video ID field is required")
        
        # Add video to playlist
        success = add_video_to_playlist(int(user_id), playlist_id, video_data["video_id"])
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to add video to playlist")
        
        return {
            "message": "Video added to playlist successfully"
        }
        
    except Exception as e:
        logger.error(f"YouTube add to playlist error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add video to playlist: {str(e)}")


@router.get("/youtube/videos/{video_id}/summary")
async def summarize_video(video_id: str, credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(get_db)):
    """Get a summary of a YouTube video"""
    try:
        # Verify token and get user ID
        token = credentials.credentials
        user_id = decode_token(token)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get video summary
        summary = get_video_summary(int(user_id), video_id)
        
        if not summary:
            raise HTTPException(status_code=404, detail="Video not found or could not be summarized")
        
        return {
            "message": "Video summary generated successfully",
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"YouTube video summary error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to summarize video: {str(e)}")


@router.get("/youtube/playlists/{playlist_id}/summary")
async def summarize_playlist(playlist_id: str, credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(get_db)):
    """Get a summary of a YouTube playlist"""
    try:
        # Verify token and get user ID
        token = credentials.credentials
        user_id = decode_token(token)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get playlist summary
        summary = get_playlist_summary(int(user_id), playlist_id)
        
        if not summary:
            raise HTTPException(status_code=404, detail="Playlist not found or could not be summarized")
        
        return {
            "message": "Playlist summary generated successfully",
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"YouTube playlist summary error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to summarize playlist: {str(e)}")


@router.get("/progress")
async def get_learning_progress(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(get_db)):
    """Get detailed learning progress for the user"""
    try:
        # Verify token and get user ID
        token = credentials.credentials
        user_id = decode_token(token)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get user information
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get learning plan
        plan = db.query(LearningPlan).filter(LearningPlan.user_id == int(user_id)).first()
        if not plan:
            raise HTTPException(status_code=404, detail="Learning plan not found")
        
        # Get progress summary
        summary = LearningPathService.get_user_progress_summary(db, int(user_id), plan.id)
        
        # Get current position details
        current_position = {
            "current_month_index": user.current_month_index,
            "current_day": user.current_day,
            "plan_title": plan.title
        }
        
        # Get detailed month progress
        months = plan.plan.get("months", []) if isinstance(plan.plan, dict) else []
        month_progress = []
        
        for month in months:
            month_data = {
                "index": month.get("index"),
                "title": month.get("title"),
                "status": month.get("status"),
                "started_at": month.get("started_at"),
                "completed_at": month.get("completed_at"),
                "days_completed": 0,
                "total_days": len(month.get("days", [])) if month.get("days") else 0
            }
            
            # Count completed days
            if month.get("days"):
                month_data["days_completed"] = sum(1 for day in month.get("days") if day.get("completed", False))
            
            month_progress.append(month_data)
        
        return {
            "current_position": current_position,
            "summary": summary,
            "month_progress": month_progress
        }
        
    except Exception as e:
        logger.error(f"Get progress error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve progress: {str(e)}")


@router.post("/linkedin/post")
async def create_linkedin_post(post_data: dict, credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(get_db)):
    """Create a LinkedIn post with AI-generated content"""
    try:
        # Verify token and get user ID
        token = credentials.credentials
        user_id = decode_token(token)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get user information
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Validate post data
        if "topic" not in post_data:
            raise HTTPException(status_code=400, detail="Topic field is required")
        
        topic = post_data["topic"]
        visibility = post_data.get("visibility", "PUBLIC")
        
        # Build user context for content generation
        context_parts = []
        
        # Add learning context
        plan = db.query(LearningPlan).filter(LearningPlan.user_id == int(user_id)).first()
        if plan:
            context_parts.append(f"Learning Plan: {plan.title}")
            context_parts.append(f"Current Progress: Day {user.current_day}, Month {user.current_month_index}")
        
        # Add onboarding context
        from app.models.onboarding import Onboarding
        onboarding = db.query(Onboarding).filter(Onboarding.user_id == int(user_id)).first()
        if onboarding:
            context_parts.append(f"Career Goals: {onboarding.career_goals}")
            context_parts.append(f"Current Skills: {onboarding.current_skills}")
        
        user_context = " ".join(context_parts)
        
        # Generate content using AI
        from app.core.composio_service import generate_linkedin_content, composio_auth
        generated_content = generate_linkedin_content(topic, user_context)
        
        # Create the LinkedIn post
        post_result = composio_auth.create_linkedin_post(user.email, generated_content, visibility)
        
        if post_result.get('success'):
            return {
                "message": "LinkedIn post created successfully",
                "content": generated_content,
                "post_id": post_result.get('post_id'),
                "topic": topic
            }
        else:
            raise HTTPException(status_code=500, detail=f"Failed to create LinkedIn post: {post_result.get('error')}")
        
    except Exception as e:
        logger.error(f"LinkedIn post creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create LinkedIn post: {str(e)}")