import os
import time
import threading
import urllib.parse
from twilio.rest import Client
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.learning_plan import LearningPlan
from app.models.quiz import QuizSubmission
from app.core.learning_path_service import LearningPathService
from app.core.config import settings
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Initialize Twilio client
try:
    twilio_sid = os.getenv("TWILIO_ACCOUNT_SID") or settings.TWILIO_ACCOUNT_SID
    twilio_token = os.getenv("TWILIO_AUTH_TOKEN") or settings.TWILIO_AUTH_TOKEN
    
    if twilio_sid and twilio_token:
        client = Client(twilio_sid, twilio_token)
        logger.info("Twilio client initialized")
    else:
        client = None
        logger.error("Twilio credentials missing")
except Exception as e:
    client = None
    logger.error(f"Twilio client init failed: {e}")

class CallMonitor:
    def __init__(self):
        self.call_sid = None
        self.call_status = "idle"
        self.conversation_log = []
        
    def log_event(self, event):
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {event}"
        print(log_entry)
        self.conversation_log.append(log_entry)
    
    def monitor_call(self, call_sid):
        """Monitor call status"""
        self.call_sid = call_sid
        self.log_event(f"Monitoring {call_sid}")
        
        while True:
            try:
                call = client.calls(call_sid).fetch()
                new_status = call.status
                
                if new_status != self.call_status:
                    self.call_status = new_status
                    self.log_event(f"Status: {new_status}")
                    
                    if new_status in ['completed', 'busy', 'failed', 'no-answer']:
                        self.log_event(f"Duration: {call.duration or 0}s")
                        break
                
                time.sleep(2)
            except Exception as e:
                self.log_event(f"Monitor error: {e}")
                break

class CallBot:
    def __init__(self):
        self.monitor = CallMonitor()
    
    def build_user_context(self, db: Session, user_id: int) -> str:
        """Build detailed context with learning plan specifics"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return "You are Abhishek's AI learning assistant. Be helpful and encouraging."
            
            user_name = "Abhishek"
            if user.google_name:
                user_name = user.google_name
            elif user.email:
                email_name = user.email.split('@')[0]
                if email_name and email_name != 'user':
                    user_name = email_name.replace('.', ' ').title()
            
            context_parts = [f"You are {user_name}'s AI learning assistant."]
            
            plan = db.query(LearningPlan).filter(LearningPlan.user_id == user_id).first()
            if plan:
                context_parts.append(f"Learning Plan: {plan.title}")
                context_parts.append(f"Currently on Day {user.current_day} of Month {user.current_month_index}")
                
                # Get detailed current topic
                if plan.plan and isinstance(plan.plan, dict) and "months" in plan.plan:
                    months = plan.plan.get("months", [])
                    if user.current_month_index <= len(months):
                        current_month = months[user.current_month_index - 1]
                        month_title = current_month.get("title", f"Month {user.current_month_index}")
                        context_parts.append(f"Current Month: {month_title}")
                        
                        days = current_month.get("days", [])
                        if user.current_day <= len(days):
                            current_day_data = days[user.current_day - 1]
                            concept = current_day_data.get('concept', '')
                            description = current_day_data.get('description', '')
                            
                            if concept:
                                context_parts.append(f"Today's Topic: {concept}")
                            if description:
                                context_parts.append(f"Description: {description[:100]}")
                            
                            # Add learning objectives if available
                            objectives = current_day_data.get('learning_objectives', [])
                            if objectives:
                                context_parts.append(f"Objectives: {', '.join(objectives[:2])}")
                
                # Progress info
                summary = LearningPathService.get_user_progress_summary(db, user_id, plan.id)
                progress = summary.get('overall_progress_percentage', 0)
                context_parts.append(f"Progress: {progress}% complete")
            
            # Recent quiz performance
            recent_quiz = db.query(QuizSubmission).filter(
                QuizSubmission.user_id == user_id
            ).order_by(QuizSubmission.created_at.desc()).first()
            
            if recent_quiz:
                status = "passed" if recent_quiz.passed else "needs improvement"
                context_parts.append(f"Last Quiz: {recent_quiz.score}% ({status})")
            
            context_parts.append("Be specific about his learning plan. Encourage progress. Keep voice responses concise.")
            return " ".join(context_parts)
            
        except Exception as e:
            logger.error(f"Context error: {e}")
            return "You are Abhishek's AI learning assistant helping with his AI Engineer learning path. Be specific and encouraging."
    
    def make_call(self, db: Session, user_id: int, to_number: str) -> dict:
        """Make call with shared context from chatbot"""
        try:
            if not client:
                return {"success": False, "error": "Twilio client not initialized"}
            
            # Get webhook URL from environment
            webhook_url = os.getenv("TWILIO_WEBHOOK_URL") or settings.TWILIO_WEBHOOK_URL
            if not webhook_url:
                return {"success": False, "error": "Webhook URL not configured"}
            
            # Build shared context (same as chatbot)
            context = self.build_user_context(db, user_id)
            encoded_context = urllib.parse.quote(context)
            full_webhook_url = f"{webhook_url}?context={encoded_context}"
            
            self.monitor.log_event(f"📱 Calling {to_number}")
            self.monitor.log_event(f"🎯 Context: {context[:50]}...")
            
            # Get Twilio phone number
            twilio_phone = os.getenv("TWILIO_PHONE_NUMBER") or settings.TWILIO_PHONE_NUMBER
            if not twilio_phone:
                return {"success": False, "error": "Twilio phone number not configured"}
            
            call = client.calls.create(
                to=to_number,
                from_=twilio_phone,
                url=full_webhook_url
            )
            
            self.monitor.log_event(f"✅ Call created: {call.sid}")
            
            # Start monitoring
            monitor_thread = threading.Thread(target=self.monitor.monitor_call, args=(call.sid,))
            monitor_thread.daemon = True
            monitor_thread.start()
            
            return {
                "success": True,
                "call_sid": call.sid,
                "status": "initiated",
                "context_preview": context[:100] + "..." if len(context) > 100 else context,
                "logs": self.monitor.conversation_log
            }
            
        except Exception as e:
            self.monitor.log_event(f"❌ Call failed: {e}")
            return {"success": False, "error": str(e), "logs": self.monitor.conversation_log}
    
    def get_call_status(self, call_sid: str) -> dict:
        """Get current call status"""
        try:
            call = client.calls(call_sid).fetch()
            return {
                "call_sid": call_sid,
                "status": call.status,
                "duration": call.duration
            }
        except Exception as e:
            return {"error": str(e)}

# Global instance
call_bot = CallBot()