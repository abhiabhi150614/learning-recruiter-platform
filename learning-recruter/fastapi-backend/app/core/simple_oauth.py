"""
Simple OAuth implementation for LinkedIn and GitHub
Since Composio API has issues, we'll implement direct OAuth
"""

import requests
import secrets
import urllib.parse
import os
from typing import Dict, Any

# OAuth configurations
LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID", "your_linkedin_client_id")
LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET", "your_linkedin_client_secret")

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "your_github_client_id")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "your_github_client_secret")

class SimpleOAuthService:
    """Simple OAuth service for LinkedIn and GitHub"""
    
    def __init__(self):
        self.states = {}  # Store OAuth states
    
    def get_linkedin_auth_url(self, user_id: str, redirect_url: str = None) -> Dict[str, Any]:
        """Generate LinkedIn OAuth URL"""
        try:
            state = secrets.token_urlsafe(32)
            self.states[state] = user_id
            
            params = {
                'response_type': 'code',
                'client_id': LINKEDIN_CLIENT_ID,
                'redirect_uri': redirect_url or 'http://localhost:3000/auth/linkedin/callback',
                'state': state,
                'scope': 'r_liteprofile r_emailaddress'
            }
            
            auth_url = 'https://www.linkedin.com/oauth/v2/authorization?' + urllib.parse.urlencode(params)
            
            return {
                "auth_url": auth_url,
                "connection_id": state,
                "status": "pending"
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "status": "error"
            }
    
    def get_github_auth_url(self, user_id: str, redirect_url: str = None) -> Dict[str, Any]:
        """Generate GitHub OAuth URL"""
        try:
            state = secrets.token_urlsafe(32)
            self.states[state] = user_id
            
            params = {
                'client_id': GITHUB_CLIENT_ID,
                'redirect_uri': redirect_url or 'http://localhost:3000/auth/github/callback',
                'state': state,
                'scope': 'user:email read:user'
            }
            
            auth_url = 'https://github.com/login/oauth/authorize?' + urllib.parse.urlencode(params)
            
            return {
                "auth_url": auth_url,
                "connection_id": state,
                "status": "pending"
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "status": "error"
            }
    
    def verify_linkedin_connection(self, user_id: str, connection_id: str, code: str = None) -> Dict[str, Any]:
        """Verify LinkedIn connection"""
        try:
            if not code:
                return {"status": "pending", "message": "Waiting for authorization code"}
            
            # Exchange code for access token
            token_data = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': 'http://localhost:3000/auth/linkedin/callback',
                'client_id': LINKEDIN_CLIENT_ID,
                'client_secret': LINKEDIN_CLIENT_SECRET
            }
            
            token_response = requests.post(
                'https://www.linkedin.com/oauth/v2/accessToken',
                data=token_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            if token_response.status_code == 200:
                token_info = token_response.json()
                access_token = token_info.get('access_token')
                
                # Get profile data
                profile_data = self.get_linkedin_profile_data(access_token)
                
                return {
                    "status": "connected",
                    "connection_id": connection_id,
                    "profile": profile_data,
                    "access_token": access_token
                }
            else:
                return {"status": "error", "error": "Failed to get access token"}
                
        except Exception as e:
            return {"error": str(e), "status": "error"}
    
    def verify_github_connection(self, user_id: str, connection_id: str, code: str = None) -> Dict[str, Any]:
        """Verify GitHub connection"""
        try:
            if not code:
                return {"status": "pending", "message": "Waiting for authorization code"}
            
            # Exchange code for access token
            token_data = {
                'client_id': GITHUB_CLIENT_ID,
                'client_secret': GITHUB_CLIENT_SECRET,
                'code': code
            }
            
            token_response = requests.post(
                'https://github.com/login/oauth/access_token',
                data=token_data,
                headers={'Accept': 'application/json'}
            )
            
            if token_response.status_code == 200:
                token_info = token_response.json()
                access_token = token_info.get('access_token')
                
                # Get profile data
                profile_data = self.get_github_profile_data(access_token)
                
                return {
                    "status": "connected",
                    "connection_id": connection_id,
                    "profile": profile_data,
                    "access_token": access_token
                }
            else:
                return {"status": "error", "error": "Failed to get access token"}
                
        except Exception as e:
            return {"error": str(e), "status": "error"}
    
    def get_linkedin_profile_data(self, access_token: str) -> Dict[str, Any]:
        """Get LinkedIn profile data"""
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            
            # Get basic profile
            profile_response = requests.get(
                'https://api.linkedin.com/v2/people/~',
                headers=headers
            )
            
            if profile_response.status_code == 200:
                profile = profile_response.json()
                
                return {
                    "name": f"{profile.get('localizedFirstName', '')} {profile.get('localizedLastName', '')}".strip(),
                    "headline": profile.get('localizedHeadline', ''),
                    "location": profile.get('location', {}).get('name', ''),
                    "industry": profile.get('industryName', ''),
                    "profile_url": f"https://linkedin.com/in/{profile.get('vanityName', '')}"
                }
            else:
                return {"error": "Failed to fetch LinkedIn profile"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def get_github_profile_data(self, access_token: str) -> Dict[str, Any]:
        """Get GitHub profile data"""
        try:
            headers = {'Authorization': f'token {access_token}'}
            
            # Get user profile
            profile_response = requests.get(
                'https://api.github.com/user',
                headers=headers
            )
            
            if profile_response.status_code == 200:
                profile = profile_response.json()
                
                return {
                    "username": profile.get('login', ''),
                    "name": profile.get('name', ''),
                    "bio": profile.get('bio', ''),
                    "location": profile.get('location', ''),
                    "company": profile.get('company', ''),
                    "public_repos": profile.get('public_repos', 0),
                    "followers": profile.get('followers', 0),
                    "following": profile.get('following', 0),
                    "profile_url": profile.get('html_url', '')
                }
            else:
                return {"error": "Failed to fetch GitHub profile"}
                
        except Exception as e:
            return {"error": str(e)}

# Global instance
simple_oauth = SimpleOAuthService()