from typing import Dict, List, Any
from sqlalchemy.orm import Session
from app.models.student_profile_summary import StudentProfileSummary
from app.models.learning_plan import LearningPlan
from app.models.onboarding import Onboarding
from app.models.quiz import Quiz, QuizSubmission
from app.core.embeddings import simple_text_embedding, cosine_similarity
from app.core.summarizer import summarize_learning
import json
from datetime import datetime, timedelta


def upsert_student_profile_summary(db: Session, user_id: int) -> None:
    # Get all user data
    onb = db.query(Onboarding).filter(Onboarding.user_id == user_id).first()
    plan = db.query(LearningPlan).filter(LearningPlan.user_id == user_id).first()
    quizzes = db.query(Quiz).filter(Quiz.user_id == user_id).all()
    
    # Extract learning plan data
    months = (plan.plan or {}).get("months", []) if plan and plan.plan else []
    months_completed = sum(1 for m in months if m.get("status") == "completed")
    months_in_progress = sum(1 for m in months if m.get("status") == "active")
    total_months = len(months)
    
    # Calculate learning progress metrics
    progress_percentage = months_completed / total_months if total_months > 0 else 0
    
    # Extract topics and derive skills
    topics = []
    completed_topics = []
    for m in months:
        month_topics = [t for t in (m.get("topics") or []) if isinstance(t, str)]
        topics.extend(month_topics)
        if m.get("status") == "completed":
            completed_topics.extend(month_topics)
    
    # Enhanced skill extraction with categorization
    all_skills = set()
    technical_skills = set()
    soft_skills = set()
    
    # Extract from topics
    for topic in topics:
        if isinstance(topic, str):
            topic_lower = topic.lower()
            all_skills.add(topic)
            
            # Categorize skills
            if any(tech in topic_lower for tech in ["python", "javascript", "react", "node", "sql", "aws", "docker", "git"]):
                technical_skills.add(topic)
            elif any(soft in topic_lower for soft in ["communication", "leadership", "teamwork", "problem solving"]):
                soft_skills.add(topic)
    
    # Extract from onboarding current skills
    if onb and onb.current_skills:
        if isinstance(onb.current_skills, list):
            for skill in onb.current_skills:
                if isinstance(skill, str):
                    all_skills.add(skill)
        elif isinstance(onb.current_skills, str):
            all_skills.add(onb.current_skills)
    
    skills = list(all_skills)[:40]  # Limit to 40 skills
    
    # Extract interests from career goals
    interests = []
    if onb and onb.career_goals:
        if isinstance(onb.career_goals, list):
            interests = [goal for goal in onb.career_goals if isinstance(goal, str)]
        elif isinstance(onb.career_goals, str):
            interests = [onb.career_goals]
    
    # Get quiz submissions for performance metrics
    quiz_submissions = db.query(QuizSubmission).filter(QuizSubmission.user_id == user_id).all()
    
    # Calculate quiz performance metrics
    quiz_scores = [q.score for q in quiz_submissions if q.score is not None]
    avg_quiz_score = sum(quiz_scores) / len(quiz_scores) if quiz_scores else 0
    total_quizzes = len(quiz_submissions)
    recent_quiz_performance = 0
    
    # Calculate recent performance (last 30 days)
    if quiz_submissions:
        recent_date = datetime.utcnow() - timedelta(days=30)
        recent_submissions = [q for q in quiz_submissions if q.created_at and q.created_at >= recent_date]
        if recent_submissions:
            recent_scores = [q.score for q in recent_submissions if q.score is not None]
            recent_quiz_performance = sum(recent_scores) / len(recent_scores) if recent_scores else 0
    
    # Calculate learning velocity (topics completed per month)
    learning_velocity = len(completed_topics) / max(months_completed, 1) if months_completed > 0 else 0
    
    # Create comprehensive profile data
    profile_data = {
        "learning_progress": progress_percentage,
        "months_completed": months_completed,
        "months_in_progress": months_in_progress,
        "total_months": total_months,
        "avg_quiz_score": avg_quiz_score,
        "recent_quiz_performance": recent_quiz_performance,
        "total_quizzes": total_quizzes,
        "learning_velocity": learning_velocity,
        "technical_skills_count": len(technical_skills),
        "soft_skills_count": len(soft_skills),
        "total_topics_learned": len(completed_topics),
        "grade": getattr(onb, "grade", None) if onb else None,
        "time_commitment": getattr(onb, "time_commitment", None) if onb else None
    }
    
    # Create enhanced summary
    onboarding_dict = {
        "name": getattr(onb, "name", None),
        "grade": getattr(onb, "grade", None),
        "career_goals": getattr(onb, "career_goals", None),
        "current_skills": getattr(onb, "current_skills", None),
        "time_commitment": getattr(onb, "time_commitment", None),
    }
    
    # Enhanced summary with performance metrics
    summary_parts = [
        summarize_learning(onboarding_dict, months_completed, ", ".join(skills)),
        f"Learning Progress: {progress_percentage:.1%} ({months_completed}/{total_months} months completed)",
        f"Quiz Performance: {avg_quiz_score:.1%} average ({total_quizzes} quizzes taken)",
        f"Learning Velocity: {learning_velocity:.1f} topics per month",
        f"Technical Skills: {len(technical_skills)}, Soft Skills: {len(soft_skills)}"
    ]
    
    summary_text = " | ".join(summary_parts)
    
    # Create comprehensive embedding
    embedding_text = f"{summary_text} | skills: {', '.join(skills)} | interests: {', '.join(interests)} | performance: {avg_quiz_score:.2f} | progress: {progress_percentage:.2f}"
    vector = simple_text_embedding(embedding_text)
    
    # Update or create profile summary
    row = db.query(StudentProfileSummary).filter(StudentProfileSummary.user_id == user_id).first()
    if row:
        row.summary_text = summary_text
        row.interests = interests
        row.skills_tags = skills
        row.vector = vector
        # Store additional profile data as JSON
        if hasattr(row, 'profile_data'):
            row.profile_data = profile_data
    else:
        row = StudentProfileSummary(
            user_id=user_id,
            summary_text=summary_text,
            interests=interests,
            skills_tags=skills,
            vector=vector,
            graph_neighbors=[]
        )
        # Add profile_data if the column exists
        if hasattr(row, 'profile_data'):
            row.profile_data = profile_data
        db.add(row)
    
    db.commit()


def get_comprehensive_user_analytics(db: Session, user_id: int) -> Dict[str, Any]:
    """Get comprehensive analytics for a user including learning patterns and predictions"""
    # Get user data
    onb = db.query(Onboarding).filter(Onboarding.user_id == user_id).first()
    plan = db.query(LearningPlan).filter(LearningPlan.user_id == user_id).first()
    quiz_submissions = db.query(QuizSubmission).filter(QuizSubmission.user_id == user_id).all()
    profile = db.query(StudentProfileSummary).filter(StudentProfileSummary.user_id == user_id).first()
    
    if not profile:
        upsert_student_profile_summary(db, user_id)
        profile = db.query(StudentProfileSummary).filter(StudentProfileSummary.user_id == user_id).first()
    
    # Calculate learning patterns
    quiz_dates = [q.created_at for q in quiz_submissions if q.created_at]
    learning_streak = 0
    if quiz_dates:
        quiz_dates.sort()
        current_date = datetime.utcnow().date()
        for i, quiz_date in enumerate(reversed(quiz_dates)):
            if (current_date - quiz_date.date()).days <= (i + 1):
                learning_streak += 1
            else:
                break
    
    # Performance trends
    quiz_scores = [(q.created_at, q.score) for q in quiz_submissions if q.score is not None and q.created_at]
    quiz_scores.sort(key=lambda x: x[0])
    
    performance_trend = "stable"
    if len(quiz_scores) >= 3:
        recent_scores = [score for _, score in quiz_scores[-3:]]
        early_scores = [score for _, score in quiz_scores[:3]]
        recent_avg = sum(recent_scores) / len(recent_scores)
        early_avg = sum(early_scores) / len(early_scores)
        
        if recent_avg > early_avg + 0.1:
            performance_trend = "improving"
        elif recent_avg < early_avg - 0.1:
            performance_trend = "declining"
    
    # Skill progression analysis
    months = (plan.plan or {}).get("months", []) if plan and plan.plan else []
    skill_progression = []
    for i, month in enumerate(months):
        if month.get("status") in ["completed", "active"]:
            topics = month.get("topics", [])
            skill_progression.append({
                "month": i + 1,
                "topics_count": len(topics),
                "status": month.get("status"),
                "skills_learned": topics[:5]  # Top 5 topics
            })
    
    return {
        "user_id": user_id,
        "summary": profile.summary_text if profile else "No summary available",
        "skills": profile.skills_tags if profile else [],
        "interests": profile.interests if profile else [],
        "learning_metrics": {
            "current_streak": learning_streak,
            "performance_trend": performance_trend,
            "total_quizzes": len(quiz_submissions),
            "avg_score": sum(q.score for q in quiz_submissions if q.score) / len([q for q in quiz_submissions if q.score]) if quiz_submissions else 0
        },
        "skill_progression": skill_progression,
        "recommendations": generate_learning_recommendations(profile, quiz_submissions, months),
        "career_readiness": assess_career_readiness(profile, quiz_submissions, months)
    }


def generate_learning_recommendations(profile, quiz_submissions, months) -> List[str]:
    """Generate personalized learning recommendations"""
    recommendations = []
    
    # Based on quiz performance
    if quiz_submissions:
        scores = [q.score for q in quiz_submissions if q.score is not None]
        if scores:
            avg_score = sum(scores) / len(scores)
            if avg_score < 70:
                recommendations.append("Focus on reviewing fundamental concepts")
            elif avg_score > 90:
                recommendations.append("Ready for advanced topics and challenges")
    
    # Based on learning progress
    completed_months = sum(1 for m in months if m.get("status") == "completed")
    total_months = len(months)
    if total_months > 0:
        progress = completed_months / total_months
        if progress < 0.3:
            recommendations.append("Increase daily learning time for better progress")
        elif progress > 0.8:
            recommendations.append("Consider exploring specialized tracks")
    
    # Based on skills
    if profile and profile.skills_tags:
        skill_count = len(profile.skills_tags)
        if skill_count < 5:
            recommendations.append("Expand your skill set with complementary technologies")
        elif skill_count > 15:
            recommendations.append("Focus on deepening expertise in core skills")
    
    return recommendations[:3]  # Top 3 recommendations


def assess_career_readiness(profile, quiz_submissions, months) -> Dict[str, Any]:
    """Assess user's readiness for career opportunities"""
    # Calculate readiness score
    progress_score = 0
    skill_score = 0
    performance_score = 0
    
    # Progress component
    if months:
        completed = sum(1 for m in months if m.get("status") == "completed")
        progress_score = min(completed / len(months), 1.0)
    
    # Skill component
    if profile and profile.skills_tags:
        skill_score = min(len(profile.skills_tags) / 10, 1.0)  # Normalize to 10 skills
    
    # Performance component
    if quiz_submissions:
        scores = [q.score for q in quiz_submissions if q.score is not None]
        if scores:
            performance_score = sum(scores) / len(scores) / 100  # Normalize to 0-1 scale
    
    # Weighted average
    overall_readiness = (progress_score * 0.4 + skill_score * 0.3 + performance_score * 0.3)
    
    # Determine readiness level
    if overall_readiness >= 0.8:
        level = "High"
        description = "Ready for senior-level positions"
    elif overall_readiness >= 0.6:
        level = "Medium"
        description = "Ready for mid-level positions"
    elif overall_readiness >= 0.4:
        level = "Entry"
        description = "Ready for entry-level positions"
    else:
        level = "Developing"
        description = "Continue learning to improve readiness"
    
    return {
        "overall_score": overall_readiness,
        "level": level,
        "description": description,
        "components": {
            "progress": progress_score,
            "skills": skill_score,
            "performance": performance_score
        }
    }


def compute_neighbors(db: Session, k: int = 10) -> None:
    """Compute AI-enhanced kNN graph based on comprehensive similarity."""
    from app.core.ai_matching import calculate_ai_match_percentage
    from app.models.job import Job
    
    all_rows = db.query(StudentProfileSummary).all()
    
    for src in all_rows:
        scored = []
        src_user = db.query(User).filter(User.id == src.user_id).first()
        
        if not src_user:
            continue
            
        for dst in all_rows:
            if src.user_id == dst.user_id:
                continue
                
            dst_user = db.query(User).filter(User.id == dst.user_id).first()
            if not dst_user:
                continue
            
            # Use both cosine similarity and AI-enhanced matching
            cosine_score = cosine_similarity(src.vector or [], dst.vector or [])
            
            # Create a mock job based on src user's profile for AI matching
            mock_job = Job(
                title=f"Position matching {src_user.google_name or 'candidate'}",
                description=src.summary_text or "General position",
                required_skills=src.skills_tags or [],
                experience_level="Mid-level",
                location="Remote",
                job_type="Full-time"
            )
            
            try:
                ai_match = calculate_ai_match_percentage(mock_job, dst, dst_user)
                ai_score = ai_match.get("match_percentage", 0) / 100.0
                
                # Combine scores (70% cosine, 30% AI)
                combined_score = (cosine_score * 0.7) + (ai_score * 0.3)
            except Exception:
                # Fallback to cosine similarity only
                combined_score = cosine_score
            
            scored.append({
                "user_id": dst.user_id, 
                "weight": float(combined_score),
                "cosine_score": float(cosine_score),
                "ai_score": float(ai_score) if 'ai_score' in locals() else 0
            })
        
        scored.sort(key=lambda x: x["weight"], reverse=True)
        src.graph_neighbors = scored[:k]
    
    db.commit()

def enhanced_candidate_matching(db: Session, job_description: str, requirements: List[str] = None) -> List[Dict[str, Any]]:
    """Enhanced candidate matching using AI-powered scoring"""
    from app.core.ai_matching import calculate_ai_match_percentage
    from app.models.job import Job
    
    # Create a temporary job object for matching
    temp_job = Job(
        title="Matching Position",
        description=job_description,
        required_skills=requirements or [],
        experience_level="Mid-level",
        location="Remote",
        job_type="Full-time"
    )
    
    # Get all candidates with profiles
    candidates = db.query(StudentProfileSummary, User).join(
        User, StudentProfileSummary.user_id == User.id
    ).filter(User.user_type == 'student').all()
    
    matches = []
    for profile, user in candidates:
        try:
            ai_match = calculate_ai_match_percentage(temp_job, profile, user)
            
            matches.append({
                "user_id": user.id,
                "name": user.google_name or user.email,
                "email": user.email,
                "ai_match": ai_match,
                "match_percentage": ai_match.get("match_percentage", 0),
                "skills": profile.skills_tags or [],
                "summary": profile.summary_text,
                "recommendation": ai_match.get("recommendation", "Consider"),
                "strengths": ai_match.get("strengths", []),
                "gaps": ai_match.get("gaps", [])
            })
        except Exception as e:
            print(f"AI matching error for user {user.id}: {e}")
            # Fallback to basic cosine similarity
            job_vec = simple_text_embedding(job_description)
            candidate_vec = profile.vector or []
            score = cosine_similarity(job_vec, candidate_vec)
            
            matches.append({
                "user_id": user.id,
                "name": user.google_name or user.email,
                "email": user.email,
                "match_percentage": int(score * 100),
                "skills": profile.skills_tags or [],
                "summary": profile.summary_text,
                "recommendation": "Consider" if score > 0.5 else "Review",
                "strengths": [],
                "gaps": []
            })
    
    # Sort by match percentage
    matches.sort(key=lambda x: x["match_percentage"], reverse=True)
    
    return matches


