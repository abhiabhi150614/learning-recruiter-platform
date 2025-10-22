import json
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from app.core.google_auth import get_google_oauth2_session
from app.models.user import User
from app.database.db import get_db
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class GoogleMeetService:
    """Service for Google Meet integration with Calendar and Gmail APIs"""
    
    def __init__(self):
        self.scopes = [
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.readonly'
        ]
    
    def _get_session_for_user(self, user_id: int):
        """Get authenticated Google session for user"""
        db = next(get_db())
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user or not user.google_id:
            raise ValueError("Google account not linked for this user")
        return get_google_oauth2_session(user.google_id)
    
    def check_calendar_availability(self, recruiter_id: int, start_time: datetime, duration_minutes: int = 60) -> Dict[str, Any]:
        """Check recruiter's calendar availability for the proposed time"""
        try:
            session = self._get_session_for_user(recruiter_id)
            end_time = start_time + timedelta(minutes=duration_minutes)
            
            # Check for conflicts in the time slot
            time_min = start_time.isoformat()
            time_max = end_time.isoformat()
            
            response = session.get(
                'https://www.googleapis.com/calendar/v3/calendars/primary/events',
                params={
                    'timeMin': time_min,
                    'timeMax': time_max,
                    'singleEvents': True,
                    'orderBy': 'startTime'
                }
            )
            
            if response.status_code == 200:
                events = response.json().get('items', [])
                conflicts = []
                
                for event in events:
                    event_start = event.get('start', {}).get('dateTime')
                    event_end = event.get('end', {}).get('dateTime')
                    
                    if event_start and event_end:
                        conflicts.append({
                            'title': event.get('summary', 'Busy'),
                            'start': event_start,
                            'end': event_end
                        })
                
                return {
                    'available': len(conflicts) == 0,
                    'conflicts': conflicts,
                    'suggested_times': self._suggest_alternative_times(recruiter_id, start_time) if conflicts else []
                }
            
            return {'available': False, 'error': 'Unable to check calendar'}
            
        except Exception as e:
            print(f"Calendar availability check error: {e}")
            return {'available': False, 'error': str(e)}
    
    def _suggest_alternative_times(self, recruiter_id: int, original_time: datetime, num_suggestions: int = 3) -> List[Dict[str, str]]:
        """Suggest alternative meeting times if the original time is not available"""
        suggestions = []
        
        # Suggest times 1 hour later, next day same time, and next day +1 hour
        alternative_times = [
            original_time + timedelta(hours=1),
            original_time + timedelta(days=1),
            original_time + timedelta(days=1, hours=1)
        ]
        
        for alt_time in alternative_times[:num_suggestions]:
            availability = self.check_calendar_availability(recruiter_id, alt_time, 60)
            if availability.get('available'):
                suggestions.append({
                    'datetime': alt_time.isoformat(),
                    'formatted': alt_time.strftime('%Y-%m-%d at %I:%M %p')
                })
        
        return suggestions
    
    def create_google_meet_event(self, recruiter_id: int, candidate_email: str, candidate_name: str, 
                                start_time: datetime, duration_minutes: int = 60, 
                                job_title: str = "Interview", notes: str = "") -> Dict[str, Any]:
        """Create a Google Calendar event with Google Meet link"""
        try:
            session = self._get_session_for_user(recruiter_id)
            end_time = start_time + timedelta(minutes=duration_minutes)
            
            # Get recruiter info
            db = next(get_db())
            recruiter = db.query(User).filter(User.id == recruiter_id).first()
            recruiter_name = recruiter.google_name or recruiter.email.split('@')[0]
            
            # Create event with Google Meet
            event = {
                'summary': f'Interview: {job_title} - {candidate_name}',
                'description': f"""
Interview Details:
• Position: {job_title}
• Candidate: {candidate_name} ({candidate_email})
• Recruiter: {recruiter_name} ({recruiter.email})
• Duration: {duration_minutes} minutes

{notes}

This meeting was automatically scheduled through EduAI Recruitment Platform.
                """.strip(),
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC'
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC'
                },
                'attendees': [
                    {'email': candidate_email, 'displayName': candidate_name},
                    {'email': recruiter.email, 'displayName': recruiter_name}
                ],
                'conferenceData': {
                    'createRequest': {
                        'requestId': f"meet_{recruiter_id}_{int(start_time.timestamp())}",
                        'conferenceSolutionKey': {
                            'type': 'hangoutsMeet'
                        }
                    }
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                        {'method': 'popup', 'minutes': 30}        # 30 minutes before
                    ]
                },
                'guestsCanModify': False,
                'guestsCanInviteOthers': False,
                'guestsCanSeeOtherGuests': True
            }
            
            # Create the event
            response = session.post(
                'https://www.googleapis.com/calendar/v3/calendars/primary/events',
                params={'conferenceDataVersion': 1},
                json=event
            )
            
            if response.status_code in (200, 201):
                event_data = response.json()
                
                # Extract Google Meet link
                meet_link = None
                conference_data = event_data.get('conferenceData', {})
                entry_points = conference_data.get('entryPoints', [])
                
                for entry_point in entry_points:
                    if entry_point.get('entryPointType') == 'video':
                        meet_link = entry_point.get('uri')
                        break
                
                # Send invitation emails
                email_sent = self._send_interview_invitation(
                    recruiter_id, candidate_email, candidate_name, 
                    start_time, duration_minutes, job_title, 
                    meet_link, event_data.get('htmlLink'), notes
                )
                
                return {
                    'success': True,
                    'event_id': event_data.get('id'),
                    'event_link': event_data.get('htmlLink'),
                    'meet_link': meet_link,
                    'calendar_event': event_data,
                    'email_sent': email_sent,
                    'message': f'Interview scheduled successfully with {candidate_name}'
                }
            else:
                return {
                    'success': False,
                    'error': f'Failed to create calendar event: {response.text}'
                }
                
        except Exception as e:
            print(f"Google Meet event creation error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _send_interview_invitation(self, recruiter_id: int, candidate_email: str, candidate_name: str,
                                 start_time: datetime, duration_minutes: int, job_title: str,
                                 meet_link: str, calendar_link: str, notes: str = "") -> bool:
        """Send interview invitation email to candidate"""
        try:
            session = self._get_session_for_user(recruiter_id)
            
            # Get recruiter info
            db = next(get_db())
            recruiter = db.query(User).filter(User.id == recruiter_id).first()
            recruiter_name = recruiter.google_name or recruiter.email.split('@')[0]
            
            # Format time
            formatted_time = start_time.strftime('%A, %B %d, %Y at %I:%M %p UTC')
            
            # Create email content
            subject = f"Interview Invitation: {job_title} Position"
            
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #4f8cff; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                    .content {{ padding: 30px; background-color: #f9f9f9; }}
                    .meeting-details {{ background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #4f8cff; }}
                    .button {{ display: inline-block; background-color: #4f8cff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px 5px; }}
                    .meet-button {{ background-color: #34a853; }}
                    .calendar-button {{ background-color: #1a73e8; }}
                    .footer {{ background-color: #e9ecef; padding: 15px; text-align: center; border-radius: 0 0 8px 8px; font-size: 12px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎯 Interview Invitation</h1>
                        <p>You're invited to an interview!</p>
                    </div>
                    
                    <div class="content">
                        <p>Dear {candidate_name},</p>
                        
                        <p>Congratulations! We would like to invite you for an interview for the <strong>{job_title}</strong> position.</p>
                        
                        <div class="meeting-details">
                            <h3>📅 Meeting Details</h3>
                            <p><strong>Position:</strong> {job_title}</p>
                            <p><strong>Date & Time:</strong> {formatted_time}</p>
                            <p><strong>Duration:</strong> {duration_minutes} minutes</p>
                            <p><strong>Interviewer:</strong> {recruiter_name}</p>
                            <p><strong>Format:</strong> Video Interview via Google Meet</p>
                            
                            {f'<p><strong>Additional Notes:</strong><br>{notes}</p>' if notes else ''}
                        </div>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{meet_link}" class="button meet-button">🎥 Join Google Meet</a>
                            <a href="{calendar_link}" class="button calendar-button">📅 Add to Calendar</a>
                        </div>
                        
                        <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107;">
                            <h4>📋 Interview Preparation Tips:</h4>
                            <ul>
                                <li>Test your camera and microphone beforehand</li>
                                <li>Ensure stable internet connection</li>
                                <li>Join the meeting 5 minutes early</li>
                                <li>Prepare questions about the role and company</li>
                                <li>Have your resume and portfolio ready to discuss</li>
                            </ul>
                        </div>
                        
                        <p>If you need to reschedule or have any questions, please reply to this email or contact me directly.</p>
                        
                        <p>We look forward to speaking with you!</p>
                        
                        <p>Best regards,<br>
                        <strong>{recruiter_name}</strong><br>
                        {recruiter.email}<br>
                        EduAI Recruitment Team</p>
                    </div>
                    
                    <div class="footer">
                        <p>This interview was scheduled through EduAI Recruitment Platform</p>
                        <p>Please do not reply to this automated email for technical issues</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Plain text version
            text_content = f"""
Interview Invitation: {job_title} Position

Dear {candidate_name},

Congratulations! We would like to invite you for an interview for the {job_title} position.

Meeting Details:
- Position: {job_title}
- Date & Time: {formatted_time}
- Duration: {duration_minutes} minutes
- Interviewer: {recruiter_name}
- Format: Video Interview via Google Meet

Google Meet Link: {meet_link}
Calendar Event: {calendar_link}

{f'Additional Notes: {notes}' if notes else ''}

Interview Preparation Tips:
- Test your camera and microphone beforehand
- Ensure stable internet connection
- Join the meeting 5 minutes early
- Prepare questions about the role and company
- Have your resume and portfolio ready to discuss

If you need to reschedule or have any questions, please reply to this email.

We look forward to speaking with you!

Best regards,
{recruiter_name}
{recruiter.email}
EduAI Recruitment Team
            """
            
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = recruiter.email
            message['To'] = candidate_email
            
            # Add text and HTML parts
            message.attach(MIMEText(text_content, 'plain'))
            message.attach(MIMEText(html_content, 'html'))
            
            # Encode and send
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            email_request = {'raw': encoded_message}
            
            response = session.post(
                'https://gmail.googleapis.com/gmail/v1/users/me/messages/send',
                json=email_request
            )
            
            return response.status_code in (200, 201)
            
        except Exception as e:
            print(f"Interview invitation email error: {e}")
            return False
    
    def get_upcoming_interviews(self, recruiter_id: int, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """Get recruiter's upcoming interviews"""
        try:
            session = self._get_session_for_user(recruiter_id)
            
            # Get events for the next week
            time_min = datetime.utcnow().isoformat()
            time_max = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat()
            
            response = session.get(
                'https://www.googleapis.com/calendar/v3/calendars/primary/events',
                params={
                    'timeMin': time_min,
                    'timeMax': time_max,
                    'singleEvents': True,
                    'orderBy': 'startTime',
                    'q': 'Interview'  # Filter for interview events
                }
            )
            
            if response.status_code == 200:
                events = response.json().get('items', [])
                interviews = []
                
                for event in events:
                    # Extract meeting details
                    start_time = event.get('start', {}).get('dateTime')
                    end_time = event.get('end', {}).get('dateTime')
                    
                    if start_time and end_time:
                        # Extract Google Meet link
                        meet_link = None
                        conference_data = event.get('conferenceData', {})
                        entry_points = conference_data.get('entryPoints', [])
                        
                        for entry_point in entry_points:
                            if entry_point.get('entryPointType') == 'video':
                                meet_link = entry_point.get('uri')
                                break
                        
                        # Extract attendees
                        attendees = []
                        for attendee in event.get('attendees', []):
                            attendees.append({
                                'email': attendee.get('email'),
                                'name': attendee.get('displayName'),
                                'response_status': attendee.get('responseStatus')
                            })
                        
                        interviews.append({
                            'event_id': event.get('id'),
                            'title': event.get('summary'),
                            'description': event.get('description'),
                            'start_time': start_time,
                            'end_time': end_time,
                            'meet_link': meet_link,
                            'calendar_link': event.get('htmlLink'),
                            'attendees': attendees,
                            'status': event.get('status')
                        })
                
                return interviews
            
            return []
            
        except Exception as e:
            print(f"Get upcoming interviews error: {e}")
            return []
    
    def cancel_interview(self, recruiter_id: int, event_id: str, reason: str = "") -> Dict[str, Any]:
        """Cancel an interview and notify attendees"""
        try:
            session = self._get_session_for_user(recruiter_id)
            
            # Get event details first
            event_response = session.get(
                f'https://www.googleapis.com/calendar/v3/calendars/primary/events/{event_id}'
            )
            
            if event_response.status_code != 200:
                return {'success': False, 'error': 'Event not found'}
            
            event_data = event_response.json()
            
            # Send cancellation emails to attendees
            attendees = event_data.get('attendees', [])
            for attendee in attendees:
                if attendee.get('email'):
                    self._send_cancellation_email(
                        recruiter_id, attendee['email'], 
                        event_data.get('summary', 'Interview'), reason
                    )
            
            # Delete the event
            delete_response = session.delete(
                f'https://www.googleapis.com/calendar/v3/calendars/primary/events/{event_id}'
            )
            
            return {
                'success': delete_response.status_code == 204,
                'message': 'Interview cancelled and attendees notified'
            }
            
        except Exception as e:
            print(f"Cancel interview error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _send_cancellation_email(self, recruiter_id: int, attendee_email: str, 
                               interview_title: str, reason: str = "") -> bool:
        """Send interview cancellation email"""
        try:
            session = self._get_session_for_user(recruiter_id)
            
            # Get recruiter info
            db = next(get_db())
            recruiter = db.query(User).filter(User.id == recruiter_id).first()
            recruiter_name = recruiter.google_name or recruiter.email.split('@')[0]
            
            subject = f"Interview Cancelled: {interview_title}"
            
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background-color: #dc3545; color: white; padding: 20px; text-align: center;">
                        <h1>Interview Cancelled</h1>
                    </div>
                    
                    <div style="padding: 20px; background-color: #f9f9f9;">
                        <p>Dear Candidate,</p>
                        
                        <p>We regret to inform you that the interview for <strong>{interview_title}</strong> has been cancelled.</p>
                        
                        {f'<p><strong>Reason:</strong> {reason}</p>' if reason else ''}
                        
                        <p>We apologize for any inconvenience this may cause. We will reach out to you soon to reschedule if appropriate.</p>
                        
                        <p>Thank you for your understanding.</p>
                        
                        <p>Best regards,<br>
                        <strong>{recruiter_name}</strong><br>
                        {recruiter.email}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create and send email
            message = MIMEMultipart()
            message['Subject'] = subject
            message['From'] = recruiter.email
            message['To'] = attendee_email
            message.attach(MIMEText(html_content, 'html'))
            
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            email_request = {'raw': encoded_message}
            
            response = session.post(
                'https://gmail.googleapis.com/gmail/v1/users/me/messages/send',
                json=email_request
            )
            
            return response.status_code in (200, 201)
            
        except Exception as e:
            print(f"Cancellation email error: {e}")
            return False
    
    def reschedule_interview(self, recruiter_id: int, event_id: str, new_start_time: datetime,
                           duration_minutes: int = 60, reason: str = "") -> Dict[str, Any]:
        """Reschedule an existing interview"""
        try:
            session = self._get_session_for_user(recruiter_id)
            
            # Get existing event
            event_response = session.get(
                f'https://www.googleapis.com/calendar/v3/calendars/primary/events/{event_id}'
            )
            
            if event_response.status_code != 200:
                return {'success': False, 'error': 'Event not found'}
            
            event_data = event_response.json()
            new_end_time = new_start_time + timedelta(minutes=duration_minutes)
            
            # Update event times
            event_data['start']['dateTime'] = new_start_time.isoformat()
            event_data['end']['dateTime'] = new_end_time.isoformat()
            
            # Update the event
            update_response = session.put(
                f'https://www.googleapis.com/calendar/v3/calendars/primary/events/{event_id}',
                json=event_data
            )
            
            if update_response.status_code == 200:
                # Send reschedule notification emails
                attendees = event_data.get('attendees', [])
                for attendee in attendees:
                    if attendee.get('email'):
                        self._send_reschedule_email(
                            recruiter_id, attendee['email'], 
                            event_data.get('summary', 'Interview'),
                            new_start_time, duration_minutes, reason
                        )
                
                return {
                    'success': True,
                    'message': 'Interview rescheduled successfully',
                    'new_time': new_start_time.isoformat()
                }
            
            return {'success': False, 'error': 'Failed to update event'}
            
        except Exception as e:
            print(f"Reschedule interview error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _send_reschedule_email(self, recruiter_id: int, attendee_email: str, 
                             interview_title: str, new_start_time: datetime,
                             duration_minutes: int, reason: str = "") -> bool:
        """Send interview reschedule notification email"""
        try:
            session = self._get_session_for_user(recruiter_id)
            
            # Get recruiter info
            db = next(get_db())
            recruiter = db.query(User).filter(User.id == recruiter_id).first()
            recruiter_name = recruiter.google_name or recruiter.email.split('@')[0]
            
            formatted_time = new_start_time.strftime('%A, %B %d, %Y at %I:%M %p UTC')
            
            subject = f"Interview Rescheduled: {interview_title}"
            
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background-color: #ffc107; color: #212529; padding: 20px; text-align: center;">
                        <h1>Interview Rescheduled</h1>
                    </div>
                    
                    <div style="padding: 20px; background-color: #f9f9f9;">
                        <p>Dear Candidate,</p>
                        
                        <p>Your interview for <strong>{interview_title}</strong> has been rescheduled.</p>
                        
                        <div style="background-color: white; padding: 15px; border-left: 4px solid #ffc107;">
                            <p><strong>New Date & Time:</strong> {formatted_time}</p>
                            <p><strong>Duration:</strong> {duration_minutes} minutes</p>
                        </div>
                        
                        {f'<p><strong>Reason for reschedule:</strong> {reason}</p>' if reason else ''}
                        
                        <p>Please update your calendar accordingly. The Google Meet link remains the same.</p>
                        
                        <p>We apologize for any inconvenience and look forward to speaking with you at the new time.</p>
                        
                        <p>Best regards,<br>
                        <strong>{recruiter_name}</strong><br>
                        {recruiter.email}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create and send email
            message = MIMEMultipart()
            message['Subject'] = subject
            message['From'] = recruiter.email
            message['To'] = attendee_email
            message.attach(MIMEText(html_content, 'html'))
            
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            email_request = {'raw': encoded_message}
            
            response = session.post(
                'https://gmail.googleapis.com/gmail/v1/users/me/messages/send',
                json=email_request
            )
            
            return response.status_code in (200, 201)
            
        except Exception as e:
            print(f"Reschedule email error: {e}")
            return False


# Global service instance
google_meet_service = GoogleMeetService()