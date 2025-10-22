import requests
import base64
import re
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

class EmailService:
    """Simple email service for recruiters to fetch job-related emails"""
    
    JOB_KEYWORDS = [
        'job', 'application', 'resume', 'cv', 'position', 'opportunity', 
        'hiring', 'career', 'interview', 'candidate', 'employment',
        'vacancy', 'role', 'work', 'apply', 'applying', 'interested',
        'developer', 'engineer', 'manager', 'analyst', 'specialist'
    ]
    
    def __init__(self):
        pass
    
    def fetch_recent_job_emails(self, access_token: str, days_back: int = 1) -> List[Dict[str, Any]]:
        """Fetch recent job-related emails from Gmail"""
        try:
            # Simple search for job-related emails
            search_query = "in:inbox (job OR application OR resume OR cv OR position OR hiring OR career)"
            
            messages_response = requests.get(
                'https://gmail.googleapis.com/gmail/v1/users/me/messages',
                headers={'Authorization': f'Bearer {access_token}'},
                params={'maxResults': 20, 'q': search_query}
            )
            
            if messages_response.status_code != 200:
                print(f"Gmail API error: {messages_response.status_code} - {messages_response.text}")
                return []
            
            messages = messages_response.json().get('messages', [])
            emails = []
            
            for message in messages[:10]:
                email_data = self._fetch_email_details(access_token, message['id'])
                if email_data:
                    emails.append(email_data)
            
            return emails
            
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []
    
    def _fetch_email_details(self, access_token: str, message_id: str) -> Optional[Dict[str, Any]]:
        """Fetch email details"""
        try:
            msg_response = requests.get(
                f'https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            
            if msg_response.status_code != 200:
                return None
            
            msg_data = msg_response.json()
            headers = msg_data.get('payload', {}).get('headers', [])
            
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            
            # Parse sender
            if '<' in sender:
                sender_name = sender.split('<')[0].strip().strip('"')
                sender_email = sender.split('<')[1].split('>')[0]
            else:
                sender_name = sender
                sender_email = sender
            
            # Extract body
            body = self._extract_body(msg_data.get('payload', {}))
            
            return {
                'id': message_id,
                'subject': subject,
                'sender_name': sender_name,
                'sender_email': sender_email,
                'content': body[:500],
                'full_content': body,
                'attachments': [],
                'received_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error fetching email: {e}")
            return None
    
    def _extract_body(self, payload: Dict) -> str:
        """Extract email body text"""
        try:
            if 'parts' in payload:
                for part in payload['parts']:
                    if part.get('mimeType') == 'text/plain':
                        data = part.get('body', {}).get('data', '')
                        if data:
                            return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
            else:
                if payload.get('mimeType') == 'text/plain':
                    data = payload.get('body', {}).get('data', '')
                    if data:
                        return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
            return "Email content could not be extracted"
        except Exception as e:
            print(f"Body extraction error: {e}")
            return "Email content extraction failed"
    
    def summarize_email_with_ai(self, email_content: str, attachments: List[Dict] = None) -> str:
        """Generate AI summary of email"""
        try:
            from app.core.gemini_ai import chatbot
            
            prompt = f"""
Summarize this job application email:

**CANDIDATE SUMMARY:**
• Name: [Extract from email]
• Email: [Extract email address]
• Position Applied: [What role they want]
• Key Skills: [List main skills mentioned]
• Experience: [Years/level of experience]
• Education: [If mentioned]
• Summary: [Brief overview]

Email content:
{email_content[:1000]}

Provide a concise summary:
"""
            
            response = chatbot.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            print(f"AI summary error: {e}")
            return f"Email summary: {email_content[:200]}..."
    
    def extract_candidate_skills(self, email_content: str, attachments: List[Dict] = None) -> List[str]:
        """Extract skills from email"""
        try:
            from app.core.gemini_ai import chatbot
            
            prompt = f"""
Extract skills from this job application email.
Return ONLY a comma-separated list, no other text.

Email:
{email_content[:1000]}

Skills:
"""
            
            response = chatbot.model.generate_content(prompt)
            skills = [s.strip() for s in response.text.split(',') if s.strip()]
            return skills[:10]
            
        except Exception as e:
            print(f"Skill extraction error: {e}")
            return []

# Global instance
email_service = EmailService()