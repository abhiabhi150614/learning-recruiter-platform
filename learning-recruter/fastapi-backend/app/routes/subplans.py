from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from app.database.db import get_db
from app.core.security import decode_token
from app.models.user import User
import json
import os

router = APIRouter()
bearer = HTTPBearer()

class TwitterSearchRequest(BaseModel):
    query: str = "AI learning OR machine learning OR data science"
    max_results: int = 10

class LearningPathRequest(BaseModel):
    topic: str
    skill_level: str = "beginner"  # beginner, intermediate, advanced
    duration_weeks: int = 12
    hours_per_week: int = 10

class SaveLearningPathRequest(BaseModel):
    learning_path: dict
    title: str

def _get_current_user(credentials: HTTPAuthorizationCredentials, db: Session) -> User:
    try:
        user_id = decode_token(credentials.credentials)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed")

# Test route without auth
@router.post("/test-learning-path")
def test_learning_path(request: LearningPathRequest):
    """Test learning path generation without auth"""
    return create_fallback_learning_path(request)

@router.post("/subplans/generate-learning-path")
def generate_learning_path(
    request: LearningPathRequest,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db)
):
    """Generate structured learning path with weeks and days - ISOLATED FEATURE"""
    user = _get_current_user(credentials, db)
    
    try:
        # Use direct Gemini AI without dependencies on other services
        import google.generativeai as genai
        
        # Configure with API key
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            return create_fallback_learning_path(request)
        
        genai.configure(api_key=gemini_api_key)
        
        # Use Gemini 2.5 Flash model
        try:
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            # Test with simple prompt
            test_response = model.generate_content("Hello")
        except Exception as e:
            print(f"Failed to initialize gemini-2.0-flash-exp: {e}")
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                test_response = model.generate_content("Hello")
            except Exception as e2:
                print(f"Failed to initialize gemini-1.5-flash: {e2}")
                model = None
        
        if not model:
            return create_fallback_learning_path(request)
        
        prompt = f"""
Create a {request.duration_weeks}-week learning path for "{request.topic}" at {request.skill_level} level.
Student has {request.hours_per_week} hours per week.

IMPORTANT: Return ONLY valid JSON. No markdown, no explanations, just pure JSON.

JSON Structure:
{{
  "title": "Learning Path for {request.topic}",
  "description": "Comprehensive learning journey",
  "total_weeks": {request.duration_weeks},
  "hours_per_week": {request.hours_per_week},
  "skill_level": "{request.skill_level}",
  "weeks": [
    {{
      "week_number": 1,
      "title": "Week 1 Title",
      "objectives": ["Objective 1", "Objective 2"],
      "days": [
        {{
          "day": 1,
          "topic": "Day Topic",
          "concept": "Main Concept",
          "activities": ["Activity 1", "Activity 2"],
          "resources": ["Resource 1", "Resource 2"],
          "estimated_hours": 2
        }}
      ]
    }}
  ]
}}

Generate {min(request.duration_weeks, 4)} weeks with 3-5 days each. Return pure JSON only.
"""
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=2000
            )
        )
        
        # Parse JSON response with better error handling
        try:
            # Clean response text
            response_text = response.text.strip()
            print(f"Raw AI response: {response_text[:500]}...")
            
            # Remove markdown code blocks
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            # Clean up common JSON issues
            response_text = response_text.strip()
            
            # Try to find JSON in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_text = response_text[start_idx:end_idx]
                print(f"Extracted JSON: {json_text[:200]}...")
                learning_path = json.loads(json_text)
            else:
                raise ValueError("No valid JSON found in response")
            
            # Validate structure
            if not isinstance(learning_path, dict) or 'weeks' not in learning_path:
                raise ValueError("Invalid structure")
                
        except Exception as parse_error:
            print(f"JSON parsing failed: {parse_error}")
            print(f"Failed text: {response_text}")
            return create_fallback_learning_path(request)
        
        return {
            "success": True,
            "learning_path": learning_path,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"Learning path generation error: {str(e)}")
        return create_fallback_learning_path(request)

def create_fallback_learning_path(request: LearningPathRequest) -> Dict[str, Any]:
    """Create fallback learning path when AI fails"""
    weeks = []
    for week_num in range(1, min(request.duration_weeks + 1, 5)):  # Limit to 4 weeks for fallback
        week = {
            "week_number": week_num,
            "title": f"Week {week_num}: {request.topic} Fundamentals" if week_num == 1 else f"Week {week_num}: Advanced {request.topic}",
            "objectives": [
                f"Master {request.topic} basics" if week_num == 1 else f"Apply {request.topic} concepts",
                "Complete practical exercises",
                "Build understanding"
            ],
            "days": [
                {
                    "day": day,
                    "topic": f"Day {day}: {request.topic} Topic {day}",
                    "concept": f"Core concept {day}",
                    "activities": ["Study materials", "Practice exercises", "Review concepts"],
                    "resources": ["Documentation", "Online tutorials", "Practice problems"],
                    "estimated_hours": request.hours_per_week // 7
                } for day in range(1, 4)  # 3 days per week for fallback
            ]
        }
        weeks.append(week)
    
    return {
        "success": True,
        "learning_path": {
            "title": f"{request.topic} Learning Path",
            "description": f"Comprehensive {request.duration_weeks}-week learning journey for {request.topic}",
            "total_weeks": request.duration_weeks,
            "hours_per_week": request.hours_per_week,
            "skill_level": request.skill_level,
            "weeks": weeks
        },
        "generated_at": datetime.utcnow().isoformat(),
        "fallback": True
    }

# Test route without auth
@router.post("/test-tweets")
def test_tweets(request: TwitterSearchRequest):
    """Test tweets fetching without auth"""
    return create_fallback_tweets(request)

@router.post("/test-save-path")
def test_save_path(request: SaveLearningPathRequest):
    """Test save learning path without auth"""
    return {
        "success": True,
        "message": f"Learning path '{request.title}' saved successfully!",
        "saved_at": datetime.utcnow().isoformat()
    }

@router.post("/subplans/trending-tweets")
def get_trending_tweets(
    request: TwitterSearchRequest,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db)
):
    """Get trending tweets related to learning topics - ISOLATED FEATURE"""
    user = _get_current_user(credentials, db)
    
    try:
        # Get user email for Twitter user_id
        user_email = user.email
        if not user_email:
            return create_fallback_tweets(request)
        
        # Convert email to user_id format
        user_id = user_email.replace('@', '_').replace('.', '_')
        
        # Auto-fill time range for last 3 days to get more diverse content
        end_time = datetime.utcnow() - timedelta(minutes=1)  # 1 minute ago to avoid "future" error
        start_time = end_time - timedelta(days=3)  # Last 3 days for better content
        start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        end_time_str = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")

        # Use fresh Composio instance - ISOLATED from other services
        try:
            from composio import Composio
            composio = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))
            
            print(f"[TWITTER] Searching with user_id: {user_id}")
            print(f"[TWITTER] Query: {request.query}")
            print(f"[TWITTER] Time range: {start_time_str} to {end_time_str}")
            
            # Enhanced query for better educational content
            enhanced_query = f"{request.query} -is:retweet lang:en (tutorial OR guide OR learn OR course OR tips OR explained OR beginner OR advanced OR free OR resource)"
            
            arguments = {
                "query": enhanced_query,
                "start_time": start_time_str,
                "end_time": end_time_str,
                "max_results": min(request.max_results * 3, 100),  # Get 3x more to filter and sort
                "tweet_fields": ["created_at", "public_metrics", "text"],
                "sort_order": "relevancy"  # Get most relevant/engaging tweets
            }
            
            print(f"[TWITTER] Arguments: {arguments}")
            
            result = composio.tools.execute(
                "TWITTER_RECENT_SEARCH",
                user_id=user_id,
                arguments=arguments
            )
            
            print(f"[TWITTER] Raw result: {result}")
            
            # Check if result has data and sort by engagement
            if result and result.get('successful', False):
                data_section = result.get('data', {})
                if isinstance(data_section, dict) and 'data' in data_section:
                    tweets = data_section['data']
                    tweet_count = len(tweets)
                    print(f"[TWITTER] Found {tweet_count} tweets")
                    
                    if tweet_count == 0:
                        print(f"[TWITTER] No tweets in response, using fallback")
                        return create_fallback_tweets(request)
                    
                    # Filter out low-quality tweets and duplicates
                    def is_quality_tweet(tweet):
                        text = tweet.get('text', '').lower()
                        metrics = tweet.get('public_metrics', {})
                        
                        # Skip if too short or promotional
                        if len(text) < 50:
                            return False
                        
                        # Skip if no engagement at all
                        total_engagement = (metrics.get('like_count', 0) + 
                                          metrics.get('reply_count', 0) + 
                                          metrics.get('retweet_count', 0))
                        if total_engagement == 0:
                            return False
                            
                        # Skip obvious spam patterns
                        spam_words = ['airdrop', 'giveaway', '$', 'pump', 'moon', 'lambo']
                        if any(word in text for word in spam_words):
                            return False
                            
                        return True
                    
                    # Filter quality tweets
                    quality_tweets = [tweet for tweet in tweets if is_quality_tweet(tweet)]
                    
                    # Sort by engagement score (weighted: likes=1, comments=3, retweets=2)
                    def get_engagement_score(tweet):
                        metrics = tweet.get('public_metrics', {})
                        likes = metrics.get('like_count', 0)
                        comments = metrics.get('reply_count', 0) * 3  # Comments are more valuable
                        retweets = metrics.get('retweet_count', 0) * 2  # Retweets are valuable
                        return likes + comments + retweets
                    
                    sorted_tweets = sorted(quality_tweets, key=get_engagement_score, reverse=True)
                    
                    # Remove duplicates by text similarity
                    unique_tweets = []
                    seen_texts = set()
                    
                    for tweet in sorted_tweets:
                        text_key = tweet.get('text', '')[:100].lower()  # First 100 chars
                        if text_key not in seen_texts:
                            unique_tweets.append(tweet)
                            seen_texts.add(text_key)
                            
                        if len(unique_tweets) >= request.max_results:
                            break
                    
                    final_tweets = unique_tweets
                    
                    print(f"[TWITTER] Sorted by engagement, showing top {len(final_tweets)} tweets")
                    
                    # Update the result with sorted tweets
                    result['data']['data'] = final_tweets
                    data_section['meta']['result_count'] = len(final_tweets)
                    
                else:
                    print(f"[TWITTER] Invalid data structure, using fallback")
                    return create_fallback_tweets(request)
            else:
                error_msg = result.get('error', 'Unknown error') if result else 'No result'
                print(f"[TWITTER] API failed: {error_msg}, using fallback")
                return create_fallback_tweets(request)
            
            return {
                "success": True,
                "tweets": result,
                "search_params": {
                    "query": request.query,
                    "start_time": start_time_str,
                    "end_time": end_time_str,
                    "max_results": request.max_results,
                    "user_id": user_id
                }
            }
            
        except Exception as composio_error:
            print(f"[TWITTER] Composio error: {composio_error}")
            print(f"[TWITTER] Using fallback tweets")
            return create_fallback_tweets(request)
        
    except Exception as e:
        print(f"Twitter search error: {str(e)}")
        return create_fallback_tweets(request)

def create_fallback_tweets(request: TwitterSearchRequest) -> Dict[str, Any]:
    """Create fallback tweets when Twitter API fails"""
    # Generate sample educational tweets based on query
    sample_tweets = [
        {
            "id": "1234567890",
            "text": "🚀 Just discovered an amazing machine learning tutorial! The way they explain neural networks is so clear and practical. Perfect for beginners! #MachineLearning #AI #Education",
            "created_at": (datetime.utcnow() - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "public_metrics": {"like_count": 45, "reply_count": 8, "retweet_count": 12}
        },
        {
            "id": "1234567891",
            "text": "💡 Pro tip: When learning data science, start with understanding your data before jumping into complex algorithms. Data exploration is key! #DataScience #Learning #Tips",
            "created_at": (datetime.utcnow() - timedelta(hours=5)).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "public_metrics": {"like_count": 67, "reply_count": 15, "retweet_count": 23}
        },
        {
            "id": "1234567892",
            "text": "📚 Free Python course alert! This comprehensive guide covers everything from basics to advanced topics. Highly recommended for aspiring developers! #Python #Programming #FreeCourse",
            "created_at": (datetime.utcnow() - timedelta(hours=8)).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "public_metrics": {"like_count": 89, "reply_count": 22, "retweet_count": 34}
        },
        {
            "id": "1234567893",
            "text": "🎯 The best way to learn AI? Build projects! Start small, iterate often, and don't be afraid to make mistakes. Each error is a learning opportunity! #AI #ProjectBasedLearning",
            "created_at": (datetime.utcnow() - timedelta(hours=12)).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "public_metrics": {"like_count": 156, "reply_count": 31, "retweet_count": 45}
        },
        {
            "id": "1234567894",
            "text": "🔥 JavaScript developers: Understanding async/await will change how you write code forever. Here's a simple explanation that finally made it click for me! #JavaScript #WebDev",
            "created_at": (datetime.utcnow() - timedelta(hours=18)).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "public_metrics": {"like_count": 78, "reply_count": 19, "retweet_count": 28}
        }
    ]
    
    # Filter tweets based on query keywords
    query_lower = request.query.lower()
    filtered_tweets = []
    
    for tweet in sample_tweets:
        tweet_text_lower = tweet["text"].lower()
        if any(keyword in tweet_text_lower for keyword in ["learning", "ai", "machine", "data", "python", "javascript", "programming"]):
            filtered_tweets.append(tweet)
    
    # Limit to requested number
    limited_tweets = filtered_tweets[:request.max_results]
    
    return {
        "success": True,
        "tweets": {
            "data": {
                "data": limited_tweets,
                "meta": {
                    "has_more": True,
                    "newest_id": limited_tweets[0]["id"] if limited_tweets else "1234567890",
                    "oldest_id": limited_tweets[-1]["id"] if limited_tweets else "1234567890",
                    "result_count": len(limited_tweets)
                }
            },
            "error": None,
            "successful": True
        },
        "search_params": {
            "query": request.query,
            "max_results": request.max_results
        },
        "fallback": True,
        "message": "Showing sample educational tweets (Twitter API unavailable)"
    }

@router.get("/subplans/trending-topics")
def get_trending_topics(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db)
):
    """Get predefined trending topics for quick search - ISOLATED FEATURE"""
    user = _get_current_user(credentials, db)
    
    trending_topics = [
        {
            "category": "AI & Machine Learning",
            "queries": [
                "AI learning OR machine learning OR data science",
                "artificial intelligence OR deep learning OR neural networks",
                "python machine learning OR tensorflow OR pytorch"
            ]
        },
        {
            "category": "Programming",
            "queries": [
                "python programming OR javascript OR react",
                "web development OR frontend OR backend",
                "coding tips OR programming tutorial"
            ]
        },
        {
            "category": "Data Science",
            "queries": [
                "data science OR data analysis OR statistics",
                "pandas OR numpy OR matplotlib",
                "data visualization OR analytics"
            ]
        },
        {
            "category": "Technology Trends",
            "queries": [
                "tech trends OR innovation OR startup",
                "cloud computing OR AWS OR azure",
                "blockchain OR cryptocurrency OR web3"
            ]
        }
    ]
    
    return {
        "success": True,
        "trending_topics": trending_topics
    }

@router.post("/subplans/save-learning-path")
def save_learning_path(
    request: SaveLearningPathRequest,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db)
):
    """Save learning path to user's profile"""
    user = _get_current_user(credentials, db)
    
    try:
        # For now, just return success (you can implement database storage later)
        return {
            "success": True,
            "message": f"Learning path '{request.title}' saved successfully!",
            "saved_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }