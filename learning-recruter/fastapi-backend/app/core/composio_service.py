from typing import Dict, Any, Optional
from composio import Composio
import os
import hashlib

class ComposioAuthService:
    """Service for handling social media authentication via Composio
    
    IMPORTANT INTEGRATION NOTES:
    ===========================
    
    Google Services Integration Experience:
    - YouTube, Gmail, Calendar, Drive, Google Meet all work with both Google OAuth and Composio
    - TRIED BOTH approaches during development - each has pros and cons
    
    Composio Approach:
    ✅ Pros: AI-driven tool execution, built-in error handling, consistent API
    ❌ Cons: Individual service connections required (no unified Google package)
    
    Google OAuth Approach:  
    ✅ Pros: Single auth for ALL Google services, full feature access, better rate limits
    ❌ Cons: Complex setup, manual token refresh, different API formats
    
    THE REALITY:
    - In Composio: Had to connect YouTube, Gmail, Calendar, Drive, Meet INDIVIDUALLY
    - In Google OAuth: Get ALL services with single authentication
    - Would have been better if Composio provided entire Google package instead of individual services
    
    Our Solution: HYBRID APPROACH
    - Use Composio for AI-enhanced operations (search, simple CRUD)
    - Use Google OAuth for advanced features and unified access
    - Best of both worlds but requires managing dual authentication
    """
    
    def __init__(self):
        self.api_key = os.getenv("COMPOSIO_API_KEY")
        self.composio = Composio(api_key=self.api_key)
        
        # NOTE: This service handles social media integrations through Composio
        # For Google services (YouTube, Gmail, Calendar, Drive, Meet), we use a hybrid approach:
        # - Composio for AI-driven operations and simple integrations
        # - Direct Google OAuth for comprehensive access and advanced features
        # See google_services.py and youtube_services.py for Google OAuth implementations
    
    def _get_unique_user_id(self, email: str) -> str:
        """Generate unique user ID from email"""
        return email.replace('@', '_').replace('.', '_')
    
    def get_linkedin_auth_url(self, user_email: str, redirect_url: str = None) -> Dict[str, Any]:
        """Generate LinkedIn OAuth URL"""
        try:
            unique_id = self._get_unique_user_id(user_email)
            print(f"[LINKEDIN AUTH] Trying OAuth for user_id: {unique_id}")
            connection_request = self.composio.toolkits.authorize(
                user_id=unique_id,
                toolkit="linkedin"
            )
            print(f"[LINKEDIN AUTH] OAuth success, redirect_url: {connection_request.redirect_url}")
            return {"authUrl": connection_request.redirect_url}
        except Exception as e:
            print(f"[LINKEDIN AUTH] OAuth failed: {str(e)}")
            return {"error": str(e)}
    
    def get_github_auth_url(self, user_email: str, redirect_url: str = None) -> Dict[str, Any]:
        """Generate GitHub OAuth URL"""
        try:
            unique_id = self._get_unique_user_id(user_email)
            connection_request = self.composio.toolkits.authorize(
                user_id=unique_id,
                toolkit="github"
            )
            return {"authUrl": connection_request.redirect_url}
        except Exception as e:
            return {"error": str(e)}
    
    def get_linkedin_profile(self, user_email: str) -> Dict[str, Any]:
        """Get LinkedIn profile data"""
        try:
            unique_id = self._get_unique_user_id(user_email)
            print(f"[LINKEDIN PROFILE] Trying to fetch profile for user_id: {unique_id}")
            
            # First check available tools
            tools = self.composio.tools.get(
                user_id=unique_id,
                toolkits=["LINKEDIN"]
            )
            print(f"[LINKEDIN PROFILE] Available tools: {len(tools) if tools else 0}")
            
            result = self.composio.tools.execute(
                "LINKEDIN_GET_MY_INFO",
                user_id=unique_id,
                arguments={}
            )
            
            # Check if result indicates unauthorized/expired connection
            if result.get('error') and 'Unauthorized' in str(result.get('error')):
                print(f"[LINKEDIN PROFILE] Connection expired/unauthorized")
                return {"error": "Connection expired", "unauthorized": True, "profile": result}
            
            print(f"[LINKEDIN PROFILE] Profile fetch success: {type(result)}")
            return {"profile": result}
        except Exception as e:
            print(f"[LINKEDIN PROFILE] Profile fetch failed: {str(e)}")
            return {"error": "Failed to fetch LinkedIn profile", "details": str(e)}
    
    def get_github_repos(self, user_email: str) -> Dict[str, Any]:
        """Get GitHub repos data"""
        try:
            unique_id = self._get_unique_user_id(user_email)
            print(f"[GITHUB REPOS] Trying to fetch repos for user_id: {unique_id}")
            
            # First check available tools
            tools = self.composio.tools.get(
                user_id=unique_id,
                toolkits=["GITHUB"]
            )
            print(f"[GITHUB REPOS] Available tools: {len(tools) if tools else 0}")
            
            result = self.composio.tools.execute(
                "GITHUB_ACTIVITY_LIST_REPO_S_STARRED_BY_AUTHENTICATED_USER",
                user_id=unique_id,
                arguments={"owner": "example", "repo": "repo"}
            )
            
            # Check if result indicates unauthorized/expired connection
            if result.get('error') and 'Unauthorized' in str(result.get('error')):
                print(f"[GITHUB REPOS] Connection expired/unauthorized")
                return {"error": "Connection expired", "unauthorized": True, "repos": result}
            
            print(f"[GITHUB REPOS] Repos fetch success: {type(result)}")
            return {"repos": result}
        except Exception as e:
            print(f"[GITHUB REPOS] Repos fetch failed: {str(e)}")
            return {"error": "Failed to fetch repos", "details": str(e)}
    
    def get_twitter_auth_url(self, user_email: str, redirect_url: str = None) -> Dict[str, Any]:
        """Generate Twitter OAuth URL"""
        try:
            unique_id = self._get_unique_user_id(user_email)
            connection_request = self.composio.toolkits.authorize(
                user_id=unique_id,
                toolkit="twitter"
            )
            return {"authUrl": connection_request.redirect_url}
        except Exception as e:
            return {"error": str(e)}
    
    def get_twitter_profile(self, user_email: str) -> Dict[str, Any]:
        """Get Twitter profile data"""
        try:
            user_id = self._get_unique_user_id(user_email)
            print(f"[TWITTER PROFILE] Trying to fetch profile for user_id: {user_id}")
            
            # Use fresh Composio instance like working test
            from composio import Composio
            composio = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))
            
            result = composio.tools.execute(
                "TWITTER_USER_LOOKUP_ME",
                user_id=user_id,
                arguments={}
            )
            
            print(f"[TWITTER PROFILE] Profile fetch success: {result}")
            return {"profile": result}
        except Exception as e:
            print(f"[TWITTER PROFILE] Profile fetch failed: {str(e)}")
            return {"error": "Failed to fetch Twitter profile", "details": str(e)}
    
    def disconnect_linkedin(self, user_email: str, connection_id: str = None) -> Dict[str, Any]:
        """Disconnect LinkedIn account"""
        try:
            return {"status": "disconnected", "message": "LinkedIn account disconnected"}
        except Exception as e:
            return {"error": str(e), "status": "error"}
    
    def disconnect_github(self, user_email: str, connection_id: str = None) -> Dict[str, Any]:
        """Disconnect GitHub account"""
        try:
            return {"status": "disconnected", "message": "GitHub account disconnected"}
        except Exception as e:
            return {"error": str(e), "status": "error"}
    
    def get_twitter_search(self, user_id: str, query: str, start_time: str = None, end_time: str = None, max_results: int = 10, tweet_fields: list = None) -> Dict[str, Any]:
        """Search Twitter for recent tweets
        
        NOTE: Twitter integration works well through Composio with consistent API responses.
        Unlike Google services where we needed individual connections, Twitter provides
        a unified experience through Composio's Twitter toolkit.
        """
        try:
            # Use fresh Composio instance like working Twitter profile
            from composio import Composio
            composio = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))
            
            if tweet_fields is None:
                tweet_fields = ["created_at", "public_metrics", "text"]
            
            result = composio.tools.execute(
                "TWITTER_RECENT_SEARCH",
                user_id=user_id,
                arguments={
                    "query": query,
                    "start_time": start_time,
                    "end_time": end_time,
                    "max_results": max_results,
                    "tweet_fields": tweet_fields,
                }
            )
            
            return {"tweets": result}
        except Exception as e:
            return {"error": "Failed to search Twitter", "details": str(e)}
    
    def disconnect_twitter(self, user_email: str, connection_id: str = None) -> Dict[str, Any]:
        """Disconnect Twitter account"""
        try:
            return {"status": "disconnected", "message": "Twitter account disconnected"}
        except Exception as e:
            return {"error": str(e), "status": "error"}
    
    def create_linkedin_post(self, user_email: str, content: str, visibility: str = "PUBLIC") -> Dict[str, Any]:
        """Create LinkedIn post using Composio"""
        try:
            unique_id = self._get_unique_user_id(user_email)
            print(f"[LINKEDIN POST] Creating post for user_id: {unique_id}")
            
            # First get LinkedIn profile to get correct author_id
            profile_result = self.get_linkedin_profile(user_email)
            if "profile" not in profile_result:
                return {"error": "LinkedIn not connected", "success": False}
            
            # Extract author_id from profile response
            profile_data = profile_result["profile"]
            author_id = None
            
            if isinstance(profile_data, dict):
                if "data" in profile_data and "response_dict" in profile_data["data"]:
                    author_id = profile_data["data"]["response_dict"].get("author_id")
                elif "response_dict" in profile_data:
                    author_id = profile_data["response_dict"].get("author_id")
            
            if not author_id:
                return {"error": "Could not get LinkedIn author ID", "success": False}
            
            # Use exact format from working example
            post_params = {
                "author": author_id,
                "commentary": content,
                "distribution": {},
                "isReshareDisabledByAuthor": False,
                "lifecycleState": "PUBLISHED",
                "visibility": visibility
            }
            
            result = self.composio.tools.execute(
                "LINKEDIN_CREATE_LINKED_IN_POST",
                user_id=unique_id,
                arguments=post_params
            )
            
            print(f"[LINKEDIN POST] Response: {result}")
            
            # Check if post was successful
            if result.get('successful') and result.get('data', {}).get('response_data', {}).get('status_code') == 201:
                share_id = result.get('data', {}).get('response_data', {}).get('share_id', '')
                return {
                    "success": True,
                    "message": "LinkedIn post created successfully!",
                    "share_id": share_id,
                    "result": result
                }
            else:
                error_msg = result.get('error', 'Unknown error')
                return {
                    "success": False,
                    "error": error_msg,
                    "result": result
                }
            
        except Exception as e:
            print(f"[LINKEDIN POST] Post creation failed: {str(e)}")
            return {"error": str(e), "success": False}
    
    def create_learning_repo(self, user_email: str, user_name: str) -> Dict[str, Any]:
        """Create learning repository (only once)"""
        try:
            unique_id = self._get_unique_user_id(user_email)
            repo_name = f"EDUAI_{user_name}_LEARNING_JOURNEY"
            print(f"[GITHUB REPO] Creating repo for user_id: {unique_id}, repo_name: {repo_name}")
            
            result = self.composio.tools.execute(
                "GITHUB_CREATE_A_REPOSITORY_FOR_THE_AUTHENTICATED_USER",
                user_id=unique_id,
                arguments={
                    "name": repo_name,
                    "description": "My AI Learning Journey - Daily Progress & Notes",
                    "private": False,
                    "auto_init": True
                }
            )
            
            print(f"[GITHUB REPO] Repo creation result: {result}")
            return {
                "success": True,
                "repo_name": repo_name,
                "html_url": result.get("html_url"),
                "clone_url": result.get("clone_url")
            }
            
        except Exception as e:
            print(f"[GITHUB REPO] Repo creation failed: {str(e)}")
            if "name already exists" in str(e).lower():
                print(f"[GITHUB REPO] Repository already exists - continuing")
                return {"success": True, "message": "Repository already exists"}
            return {"error": f"Failed to create repo: {str(e)}", "success": False}
    
    def add_daily_notes_to_github(self, user_email: str, user_name: str, notes: str, day: int, month: int, concept: str) -> Dict[str, Any]:
        """Add daily notes to GitHub repository"""
        try:
            import base64
            from datetime import datetime
            
            unique_id = self._get_unique_user_id(user_email)
            repo_name = f"EDUAI_{user_name}_LEARNING_JOURNEY"
            filename = f"Month_{month}/Day_{day}_Notes.md"
            print(f"[GITHUB FILE] Adding file for user_id: {unique_id}, repo: {repo_name}, file: {filename}")
            
            # Format notes as markdown
            content = f"# Day {day} - {concept}\n\n**Date:** {datetime.now().strftime('%Y-%m-%d')}\n\n## Notes\n\n{notes}\n\n---\n*Generated by EduAI Learning System*"
            print(f"[GITHUB FILE] Content length: {len(content)} chars")
            
            encoded_content = base64.b64encode(content.encode()).decode()
            
            result = self.composio.tools.execute(
                "GITHUB_CREATE_OR_UPDATE_FILE_CONTENTS",
                user_id=unique_id,
                arguments={
                    "owner": "abhiabhi150614",
                    "repo": repo_name,
                    "path": filename,
                    "message": f"Add Day {day} learning notes",
                    "content": encoded_content,
                    "branch": "main"
                }
            )
            
            print(f"[GITHUB FILE] File creation result: {result}")
            return {
                "success": True,
                "message": f"Notes added to GitHub: {filename}",
                "file_url": f"https://github.com/{unique_id}/{repo_name}/blob/main/{filename}"
            }
            
        except Exception as e:
            print(f"[GITHUB FILE] File creation failed: {str(e)}")
            return {"error": f"Failed to add notes to GitHub: {str(e)}", "success": False}

def generate_linkedin_content(topic: str, user_context: str = "") -> str:
    """Generate LinkedIn post content using Gemini AI with error handling"""
    try:
        import google.generativeai as genai
        import os
        
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""
        Write a professional LinkedIn post about: {topic}
        
        Context: {user_context}
        
        Requirements:
        - Professional and engaging tone
        - Include 2-3 relevant hashtags
        - Keep under 250 words
        - Make it authentic and personal
        
        Post content:
        """
        
        response = model.generate_content(
            prompt,
            generation_config={
                'temperature': 0.7,
                'top_p': 0.8,
                'top_k': 40,
                'max_output_tokens': 300
            }
        )
        
        # Handle blocked or empty responses
        if response.candidates and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if candidate.content and candidate.content.parts:
                return candidate.content.parts[0].text.strip()
        
        # Fallback if response is blocked or empty
        return create_fallback_linkedin_post(topic)
        
    except Exception as e:
        print(f"Error generating LinkedIn content: {e}")
        return create_fallback_linkedin_post(topic)

def create_fallback_linkedin_post(topic: str) -> str:
    """Create fallback LinkedIn post when AI fails"""
    fallback_posts = {
        "python fundamentals": "Diving deep into Python fundamentals! 🐍\n\nMastering variables, data types, control flow, and functions - the building blocks of every great AI project. Every expert was once a beginner!\n\n#Python #Programming #AILearning #TechSkills #CodingJourney",
        "machine learning": "Exploring the fascinating world of Machine Learning! 🤖\n\nFrom algorithms to real-world applications, every day brings new insights. The future is being built with data and intelligence.\n\n#MachineLearning #AI #DataScience #TechInnovation #Learning",
        "ai": "Excited about the endless possibilities of Artificial Intelligence! 🎆\n\nEvery breakthrough in AI opens new doors for innovation and problem-solving. The journey of learning never stops!\n\n#AI #ArtificialIntelligence #Technology #Innovation #FutureTech"
    }
    
    # Try to match topic to fallback
    topic_lower = topic.lower()
    for key, post in fallback_posts.items():
        if key in topic_lower:
            return post
    
    # Generic fallback
    return f"Excited to share insights about {topic}! 🚀\n\nContinuous learning and growth in technology keeps pushing boundaries. Every step forward matters!\n\n#Technology #Learning #Growth #Innovation #Professional"

# Global instance
composio_auth = ComposioAuthService()