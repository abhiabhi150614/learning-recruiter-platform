from sqlalchemy.orm import Session
from typing import Dict, List, Any
from datetime import datetime
from app.models.user import User
from app.models.onboarding import Onboarding
from app.models.learning_plan import LearningPlan
from app.models.candidate_vector import CandidateVector
from app.models.quiz import Quiz
from app.core.embeddings import simple_text_embedding
from app.core.summarizer import summarize_learning


class CandidateService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_candidate_summary(self, user_id: int) -> Dict[str, Any]:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
            
        onboarding = self.db.query(Onboarding).filter(Onboarding.user_id == user_id).first()
        learning_plan = self.db.query(LearningPlan).filter(LearningPlan.user_id == user_id).first()
        quizzes = self.db.query(Quiz).filter(Quiz.user_id == user_id).all()
        
        months = []
        skills = []
        if learning_plan and learning_plan.plan:
            months = learning_plan.plan.get("months", [])
            for month in months:
                if month.get("status") in ["active", "completed"]:
                    month_skills = month.get("topics", [])
                    skills.extend([skill for skill in month_skills if isinstance(skill, str)])
        
        completed_months = sum(1 for m in months if m.get("status") == "completed")
        total_months = len(months)
        progress_percentage = (completed_months / total_months * 100) if total_months > 0 else 0
        
        quiz_scores = [q.score for q in quizzes if q.score is not None]
        avg_quiz_score = sum(quiz_scores) / len(quiz_scores) if quiz_scores else 0
        
        profile_data = {
            "user_id": user_id,
            "name": getattr(onboarding, "name", f"User {user_id}"),
            "email": getattr(user, "email", ""),
            "skills": list(set(skills))[:20],
            "learning_progress": progress_percentage,
            "avg_quiz_score": avg_quiz_score,
            "career_readiness": self._assess_career_readiness(progress_percentage, avg_quiz_score, len(skills))
        }
        
        summary_text = f"{profile_data['name']} - Progress: {progress_percentage:.1f}%, Skills: {', '.join(skills[:5])}"
        vector = simple_text_embedding(summary_text)
        
        existing = self.db.query(CandidateVector).filter(CandidateVector.user_id == user_id).first()
        if existing:
            existing.vector = vector
            existing.summary_text = summary_text
            existing.skills_tags = profile_data['skills']
            existing.updated_at = datetime.utcnow()
        else:
            candidate_vector = CandidateVector(
                user_id=user_id,
                vector=vector,
                summary_text=summary_text,
                skills_tags=profile_data['skills']
            )
            self.db.add(candidate_vector)
        
        self.db.commit()
        return profile_data
    
    def _assess_career_readiness(self, progress: float, quiz_score: float, skill_count: int) -> str:
        readiness_score = (progress * 0.4) + (quiz_score * 0.4) + (min(skill_count, 10) * 2)
        
        if readiness_score >= 80:
            return "High"
        elif readiness_score >= 60:
            return "Medium"
        else:
            return "Developing"