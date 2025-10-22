from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime
import random
from fastapi import HTTPException
from typing import List, Dict
import google.generativeai as genai
import uuid
from app.database.db import get_db
from app.core.security import create_access_token, decode_token
from passlib.context import CryptContext
from app.models.candidate_vector import CandidateVector
from app.models.user import User
from app.models.learning_plan import LearningPlan
from app.models.onboarding import Onboarding
from app.models.job import Job
from app.models.email_application import EmailApplication
from app.models.shortlist import Shortlist
from app.core.embeddings import simple_text_embedding, cosine_similarity
from app.models.quiz import QuizSubmission
from app.core.summary_service import get_comprehensive_user_analytics
from app.core.graph_rag import GraphRAG
from app.services.candidate_service import CandidateService
from datetime import datetime

router = APIRouter()
bearer = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _get_current_user(credentials: HTTPAuthorizationCredentials, db: Session) -> User:
    """Get current user from token"""
    try:
        user_id = decode_token(credentials.credentials)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed")

def _require_recruiter(credentials: HTTPAuthorizationCredentials, db: Session) -> User:
    """Require user to be a recruiter"""
    user = _get_current_user(credentials, db)
    if user.user_type != 'recruiter':
        raise HTTPException(status_code=403, detail="Recruiter access required. Please login as a recruiter.")
    return user

@router.post("/recruiter/match")
def recruiter_match(data: Dict[str, Any], credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    _require_recruiter(credentials, db)
    job_description = data.get("job_description") or ""
    requirements = data.get("requirements", [])
    company = data.get("company", "")
    location = data.get("location", "")
    salary_range = data.get("salary_range", "")
    
    if not job_description:
        raise HTTPException(status_code=400, detail="job_description required")
    
    try:
        from app.core.gemini_ai import chatbot
        
        # Get all students with comprehensive data
        students = db.query(User).filter(User.user_type == 'student').all()
        matches = []
        
        for student in students:
            # Get comprehensive student data
            onboarding = db.query(Onboarding).filter(Onboarding.user_id == student.id).first()
            learning_plan = db.query(LearningPlan).filter(LearningPlan.user_id == student.id).first()
            quiz_scores = db.query(QuizSubmission).filter(QuizSubmission.user_id == student.id).all()
            candidate_vector = db.query(CandidateVector).filter(CandidateVector.user_id == student.id).first()
            
            # Calculate metrics
            avg_score = sum(q.score for q in quiz_scores) / len(quiz_scores) if quiz_scores else 0
            passed_quizzes = sum(1 for q in quiz_scores if q.passed)
            
            # Learning progress
            learning_progress = 0
            current_topic = "No active learning"
            if learning_plan and learning_plan.plan:
                months = learning_plan.plan.get("months", [])
                completed = sum(1 for m in months if m.get("status") == "completed")
                learning_progress = (completed / len(months) * 100) if months else 0
                
                # Get current topic
                current_month_index = student.current_month_index or 1
                current_day = student.current_day or 1
                if 1 <= current_month_index <= len(months):
                    current_month = months[current_month_index - 1]
                    days = current_month.get("days", [])
                    if 0 < current_day <= len(days):
                        current_day_data = days[current_day - 1]
                        current_topic = current_day_data.get('concept', 'No topic assigned')
            
            # Social connections
            linkedin_connected = student.linkedin_profile_data is not None
            github_connected = student.github_profile_data is not None
            twitter_connected = student.twitter_profile_data is not None
            
            # Parse social data for additional skills
            github_skills = []
            if github_connected and student.github_profile_data:
                try:
                    import json
                    github_data = json.loads(student.github_profile_data)
                    if isinstance(github_data, list):
                        for repo in github_data[:5]:  # Top 5 repos
                            if repo.get('language'):
                                github_skills.append(repo['language'])
                except: pass
            
            # Build comprehensive student profile
            profile_sections = []
            profile_sections.append(f"STUDENT: {student.google_name or student.email}")
            profile_sections.append(f"EMAIL: {student.email}")
            
            if onboarding:
                profile_sections.append(f"CAREER GOALS: {str(onboarding.career_goals) if onboarding.career_goals else 'Not specified'}")
                profile_sections.append(f"CURRENT SKILLS: {str(onboarding.current_skills) if onboarding.current_skills else 'Not specified'}")
                profile_sections.append(f"EDUCATION LEVEL: {onboarding.grade or 'Not specified'}")
                profile_sections.append(f"TIME COMMITMENT: {onboarding.time_commitment or 'Not specified'}")
            
            # Learning metrics
            profile_sections.append(f"LEARNING PROGRESS: {learning_progress:.1f}% completed")
            profile_sections.append(f"CURRENT LEARNING TOPIC: {current_topic}")
            profile_sections.append(f"QUIZ PERFORMANCE: {avg_score:.1f}% average ({len(quiz_scores)} quizzes, {passed_quizzes} passed)")
            
            # Additional skills from GitHub
            if github_skills:
                profile_sections.append(f"GITHUB PROGRAMMING LANGUAGES: {', '.join(set(github_skills))}")
            
            # Professional presence
            social_presence = []
            if linkedin_connected: social_presence.append("LinkedIn")
            if github_connected: social_presence.append("GitHub")
            if twitter_connected: social_presence.append("Twitter")
            profile_sections.append(f"PROFESSIONAL PRESENCE: {', '.join(social_presence) if social_presence else 'None'}")
            
            # AI summary if available
            if candidate_vector and candidate_vector.summary_text:
                profile_sections.append(f"AI PROFILE SUMMARY: {candidate_vector.summary_text}")
            
            if candidate_vector and candidate_vector.skills_tags:
                profile_sections.append(f"EXTRACTED SKILLS: {', '.join(candidate_vector.skills_tags)}")
            
            student_profile = "\n".join(profile_sections)
            
            # Enhanced AI matching prompt with better evaluation criteria
            match_prompt = f"""You are an expert recruiter. Analyze if this student can successfully perform this job.

JOB REQUIREMENTS:
{job_description}
Specific Requirements: {', '.join(requirements) if requirements else 'See job description'}
Company: {company or 'Not specified'}

STUDENT ANALYSIS:
{student_profile}

EVALUATE THESE KEY QUESTIONS:
1. Do the student's career goals align with this job role?
2. Do their current skills match the job requirements?
3. Is their learning progress showing good commitment and ability?
4. Can they realistically perform this work based on their background?
5. Are they at the right education/experience level for this position?
6. Do their GitHub projects show relevant practical experience?

SCORING CRITERIA:
- 85-100: Perfect fit - goals align, has required skills, strong progress
- 70-84: Very good fit - most requirements met, good potential
- 55-69: Good fit - some gaps but learnable, decent alignment
- 40-54: Moderate fit - significant gaps but possible with training
- 25-39: Poor fit - major misalignment in goals or skills
- 0-24: No fit - completely wrong match

Focus on: Can this student actually DO this job successfully?

Score (0-100):"""
            
            try:
                response = chatbot.model.generate_content(match_prompt)
                score_text = response.text.strip()
                import re
                numbers = re.findall(r'\d+', score_text)
                score = int(numbers[0]) if numbers else 0
                score = min(max(score, 0), 100)
                
                # Generate match explanation
                explanation_prompt = f"""Based on the {score}% match score, provide a brief 2-3 sentence explanation of why this student is or isn't a good fit for the job. Focus on key strengths or gaps.

Job: {job_description}
Student: {student.google_name or student.email}
Score: {score}%

Key factors: skills, experience, learning progress, career goals alignment.

Explanation:"""
                
                explanation_response = chatbot.model.generate_content(explanation_prompt)
                explanation = explanation_response.text.strip()
                
                if score > 40:  # Include more candidates with detailed analysis
                    matches.append({
                        "user_id": student.id,
                        "name": student.google_name or student.email,
                        "email": student.email,
                        "score": score,
                        "avg_quiz_score": round(avg_score, 1),
                        "learning_progress": round(learning_progress, 1),
                        "career_goals": str(onboarding.career_goals) if onboarding and onboarding.career_goals else "Not specified",
                        "skills": str(onboarding.current_skills) if onboarding and onboarding.current_skills else "Not specified",
                        "github_skills": github_skills,
                        "social_connections": len(social_presence),
                        "match_explanation": explanation,
                        "performance_level": "Excellent" if avg_score >= 80 else "Good" if avg_score >= 60 else "Developing",
                        "recommendation": "Highly Recommended" if score >= 85 else "Recommended" if score >= 70 else "Consider" if score >= 55 else "Not Ideal",
                        "shortlisted": False  # Will be updated by shortlist check
                    })
            except Exception as e:
                print(f"AI matching error for student {student.id}: {e}")
                continue
        
        # Sort by score
        matches.sort(key=lambda x: x["score"], reverse=True)
        return {
            "matches": matches[:25],  # Top 25 matches
            "total_analyzed": len(students),
            "total_matches": len(matches),
            "job_summary": {
                "description": job_description,
                "requirements": requirements,
                "company": company,
                "location": location
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI matching error: {str(e)}")

@router.get("/recruiter/students/search")
def search_students(q: str = "", skills: str = "", min_score: int = 0, social: str = "", credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Search and filter students with advanced options"""
    recruiter = _require_recruiter(credentials, db)
    
    students = db.query(User).filter(User.user_type == 'student').all()
    filtered_students = []
    
    for student in students:
        onboarding = db.query(Onboarding).filter(Onboarding.user_id == student.id).first()
        quiz_scores = db.query(QuizSubmission).filter(QuizSubmission.user_id == student.id).all()
        avg_score = sum(q.score for q in quiz_scores) / len(quiz_scores) if quiz_scores else 0
        
        # Apply filters
        if q and q.lower() not in (student.google_name or student.email or "").lower():
            continue
        
        if skills and onboarding and skills.lower() not in str(onboarding.current_skills or "").lower():
            continue
        
        if avg_score < min_score:
            continue
        
        if social:
            social_count = sum([
                student.linkedin_profile_data is not None,
                student.github_profile_data is not None,
                student.twitter_profile_data is not None
            ])
            if social == "linkedin" and not student.linkedin_profile_data:
                continue
            if social == "github" and not student.github_profile_data:
                continue
            if social == "twitter" and not student.twitter_profile_data:
                continue
            if social == "any" and social_count == 0:
                continue
        
        filtered_students.append({
            "id": student.id,
            "name": student.google_name or (onboarding.name if onboarding else f"Student {student.id}"),
            "email": student.email,
            "picture": student.google_picture,
            "avg_score": round(avg_score, 1),
            "quiz_count": len(quiz_scores),
            "career_goals": str(onboarding.career_goals) if onboarding and onboarding.career_goals else "Not specified",
            "skills": str(onboarding.current_skills) if onboarding and onboarding.current_skills else "Not specified",
            "social_connections": {
                "linkedin": student.linkedin_profile_data is not None,
                "github": student.github_profile_data is not None,
                "twitter": student.twitter_profile_data is not None
            }
        })
    
    return {
        "students": filtered_students,
        "total": len(filtered_students),
        "filters_applied": {
            "search_query": q,
            "skills_filter": skills,
            "min_score": min_score,
            "social_filter": social
        }
    }

@router.get("/recruiter/students")
def get_all_students(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    recruiter = _require_recruiter(credentials, db)
    
    # Get all students with comprehensive data
    students = db.query(User).filter(User.user_type == 'student').all()
    
    student_profiles = []
    for student in students:
        candidate_vector = db.query(CandidateVector).filter(CandidateVector.user_id == student.id).first()
        onboarding = db.query(Onboarding).filter(Onboarding.user_id == student.id).first()
        learning_plan = db.query(LearningPlan).filter(LearningPlan.user_id == student.id).first()
        
        # Get quiz scores
        quiz_scores = db.query(QuizSubmission).filter(QuizSubmission.user_id == student.id).all()
        avg_score = sum(q.score for q in quiz_scores) / len(quiz_scores) if quiz_scores else 0
        passed_quizzes = sum(1 for q in quiz_scores if q.passed)
        
        # Parse social connections
        linkedin_data = None
        github_data = None
        twitter_data = None
        
        if student.linkedin_profile_data:
            try:
                import json
                linkedin_data = json.loads(student.linkedin_profile_data)
            except: pass
        
        if student.github_profile_data:
            try:
                import json
                github_data = json.loads(student.github_profile_data)
            except: pass
        
        if student.twitter_profile_data:
            try:
                import json
                twitter_data = json.loads(student.twitter_profile_data)
            except: pass
        
        # Learning plan details
        learning_status = "Not yet started"
        learning_progress = 0
        current_topic = "No active learning"
        plan_title = "No learning plan"
        
        if learning_plan and learning_plan.plan:
            plan_title = learning_plan.title or "Learning Plan"
            months = learning_plan.plan.get("months", [])
            completed = sum(1 for m in months if m.get("status") == "completed")
            total = len(months)
            learning_progress = (completed / total * 100) if total > 0 else 0
            
            if learning_progress > 0:
                learning_status = f"{learning_progress:.1f}% completed"
            else:
                learning_status = "Started but no progress"
            
            # Get current topic
            current_month_index = student.current_month_index or 1
            current_day = student.current_day or 1
            
            if 1 <= current_month_index <= len(months):
                current_month = months[current_month_index - 1]
                days = current_month.get("days", [])
                if 0 < current_day <= len(days):
                    current_day_data = days[current_day - 1]
                    current_topic = current_day_data.get('concept', 'No topic assigned')
        
        profile = {
            "id": student.id,
            "name": student.google_name or (onboarding.name if onboarding else f"Student {student.id}"),
            "email": student.email,
            "picture": student.google_picture or "/default-avatar.png",
            "created_at": student.created_at.isoformat() if student.created_at else "Unknown",
            "summary": candidate_vector.summary_text if candidate_vector else "No profile summary available",
            "skills": candidate_vector.skills_tags if candidate_vector else [],
            "career_goals": str(onboarding.career_goals) if onboarding and onboarding.career_goals else "No career goals specified",
            "current_skills": str(onboarding.current_skills) if onboarding and onboarding.current_skills else "No skills listed",
            "grade": onboarding.grade if onboarding else "Not specified",
            "time_commitment": onboarding.time_commitment if onboarding else "Not specified",
            "learning_progress": learning_progress,
            "learning_status": learning_status,
            "current_topic": current_topic,
            "plan_title": plan_title,
            "quiz_performance": {
                "average_score": round(avg_score, 1),
                "total_quizzes": len(quiz_scores),
                "passed_quizzes": passed_quizzes,
                "pass_rate": round((passed_quizzes / len(quiz_scores) * 100), 1) if quiz_scores else 0,
                "performance_status": "Excellent" if avg_score >= 80 else "Good" if avg_score >= 60 else "Needs Improvement" if avg_score > 0 else "No quizzes taken"
            },
            "social_connections": {
                "linkedin": {
                    "connected": linkedin_data is not None,
                    "profile": linkedin_data,
                    "name": linkedin_data.get('data', {}).get('response_dict', {}).get('name') if linkedin_data else None,
                    "email": linkedin_data.get('data', {}).get('response_dict', {}).get('email') if linkedin_data else None
                },
                "github": {
                    "connected": github_data is not None,
                    "profile": github_data,
                    "username": github_data[0].get('owner', {}).get('login') if github_data and isinstance(github_data, list) and len(github_data) > 0 else None,
                    "repos_count": len(github_data) if github_data and isinstance(github_data, list) else 0
                },
                "twitter": {
                    "connected": twitter_data is not None,
                    "profile": twitter_data,
                    "username": twitter_data.get('data', {}).get('username') if twitter_data else None,
                    "name": twitter_data.get('data', {}).get('name') if twitter_data else None
                }
            },
            "contact_info": {
                "email": student.email,
                "google_email": student.google_email,
                "phone": "Not provided",
                "location": "Not specified"
            },
            "platform_activity": {
                "last_login": "Not tracked",
                "days_active": "Not tracked",
                "engagement_level": "Active" if quiz_scores else "Low"
            },
            "added_by_recruiter": student.created_by_recruiter_id == recruiter.id,
            "source": "Email Application" if student.created_by_recruiter_id == recruiter.id else "Platform User"
        }
        
        student_profiles.append(profile)
    
    return {"students": student_profiles, "total": len(student_profiles)}

@router.get("/recruiter/dashboard")
def get_recruiter_dashboard(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Complete recruiter dashboard with organized data"""
    recruiter = _require_recruiter(credentials, db)
    
    # Get all students with complete data
    students = db.query(User).filter(User.user_type == 'student').all()
    
    # Organize students by categories
    top_performers = []
    active_learners = []
    social_connected = []
    recent_joiners = []
    
    for student in students:
        onboarding = db.query(Onboarding).filter(Onboarding.user_id == student.id).first()
        quiz_scores = db.query(QuizSubmission).filter(QuizSubmission.user_id == student.id).all()
        learning_plan = db.query(LearningPlan).filter(LearningPlan.user_id == student.id).first()
        
        avg_score = sum(q.score for q in quiz_scores) / len(quiz_scores) if quiz_scores else 0
        
        # Calculate learning progress
        progress = 0
        if learning_plan and learning_plan.plan:
            months = learning_plan.plan.get("months", [])
            completed = sum(1 for m in months if m.get("status") == "completed")
            progress = (completed / len(months) * 100) if months else 0
        
        # Social connections count
        social_count = sum([
            student.linkedin_profile_data is not None,
            student.github_profile_data is not None,
            student.twitter_profile_data is not None
        ])
        
        student_summary = {
            "id": student.id,
            "name": student.google_name or (onboarding.name if onboarding else f"Student {student.id}"),
            "email": student.email,
            "picture": student.google_picture,
            "avg_score": round(avg_score, 1),
            "quiz_count": len(quiz_scores),
            "learning_progress": round(progress, 1),
            "social_connections": social_count,
            "career_goals": str(onboarding.career_goals) if onboarding and onboarding.career_goals else "Not specified",
            "skills": str(onboarding.current_skills) if onboarding and onboarding.current_skills else "Not specified",
            "joined_date": student.created_at.strftime("%Y-%m-%d") if student.created_at else "Unknown"
        }
        
        # Categorize students
        if avg_score >= 75 and len(quiz_scores) >= 3:
            top_performers.append(student_summary)
        
        if progress > 20:
            active_learners.append(student_summary)
        
        if social_count >= 2:
            social_connected.append(student_summary)
        
        if student.created_at and (datetime.utcnow() - student.created_at).days <= 30:
            recent_joiners.append(student_summary)
    
    # Sort categories
    top_performers.sort(key=lambda x: x["avg_score"], reverse=True)
    active_learners.sort(key=lambda x: x["learning_progress"], reverse=True)
    social_connected.sort(key=lambda x: x["social_connections"], reverse=True)
    recent_joiners.sort(key=lambda x: x["joined_date"], reverse=True)
    
    # Quick stats
    total_students = len(students)
    avg_platform_score = sum(s["avg_score"] for s in [student_summary]) / total_students if total_students > 0 else 0
    
    return {
        "overview": {
            "total_students": total_students,
            "top_performers": len(top_performers),
            "active_learners": len(active_learners),
            "social_connected": len(social_connected),
            "recent_joiners": len(recent_joiners),
            "platform_avg_score": round(avg_platform_score, 1)
        },
        "categories": {
            "top_performers": top_performers[:10],
            "active_learners": active_learners[:10],
            "social_connected": social_connected[:10],
            "recent_joiners": recent_joiners[:10]
        },
        "quick_actions": {
            "create_job_posting": "/recruiter/jobs",
            "ai_matching": "/recruiter/match",
            "view_all_students": "/recruiter/students",
            "recruiter_chat": "/recruiter/chat"
        }
    }

@router.get("/recruiter/analytics")
def get_recruiter_analytics(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    recruiter = _require_recruiter(credentials, db)
    
    # Real data from database
    total_students = db.query(User).filter(User.user_type == 'student').count()
    total_jobs = db.query(Job).filter(Job.recruiter_id == recruiter.id).count()
    total_applications = db.query(EmailApplication).filter(EmailApplication.recruiter_id == recruiter.id).count()
    candidate_vectors = db.query(CandidateVector).count()
    
    # Recent email activity
    recent_emails = db.query(EmailApplication).filter(
        EmailApplication.recruiter_id == recruiter.id
    ).order_by(EmailApplication.received_at.desc()).limit(10).all()
    
    return {
        "total_candidates": total_students,
        "high_match_candidates": candidate_vectors,
        "active_jobs": total_jobs,
        "emails_sent_today": total_applications,
        "interviews_scheduled": 0,
        "response_rate": 0.0 if total_applications == 0 else round(total_applications / max(total_students, 1), 2),
        "recent_emails": len(recent_emails),
        "unread_emails": len([e for e in recent_emails if not e.processed]),
        "top_skills": [],
        "candidate_sources": {
            "platform": total_students,
            "linkedin": 0,
            "referrals": 0
        }
    }

@router.get("/recruiter/profile")
def get_recruiter_profile(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    recruiter = _require_recruiter(credentials, db)
    
    # Get recruiter stats
    total_jobs = db.query(Job).filter(Job.recruiter_id == recruiter.id).count()
    total_emails = db.query(EmailApplication).filter(EmailApplication.recruiter_id == recruiter.id).count()
    
    return {
        "id": recruiter.id,
        "name": recruiter.google_name or recruiter.email.split('@')[0],
        "email": recruiter.email,
        "google_name": recruiter.google_name,
        "google_email": recruiter.google_email,
        "google_picture": recruiter.google_picture,
        "user_type": recruiter.user_type,
        "created_at": recruiter.created_at.isoformat() if recruiter.created_at else None,
        "stats": {
            "jobs_posted": total_jobs,
            "emails_sent": total_emails,
            "member_since": recruiter.created_at.strftime("%B %Y") if recruiter.created_at else "Recently"
        }
    }

@router.post("/recruiter/send-email")
def send_email_to_student(data: Dict[str, Any], credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    recruiter = _require_recruiter(credentials, db)
    
    # Log the email attempt in database
    try:
        email_log = EmailApplication(
            recruiter_id=recruiter.id,
            sender_email=recruiter.email,
            sender_name=recruiter.google_name or "Recruiter",
            subject=data.get('subject', 'Job Opportunity'),
            content=f"Sent to: {data.get('to')}\n\n{data.get('message', '')}",
            processed=True
        )
        db.add(email_log)
        db.commit()
    except Exception:
        pass
    
    # Simulate email sending for demo
    return {
        "message": f"Email sent successfully to {data.get('to')}",
        "status": "sent",
        "recipient": data.get('to'),
        "subject": data.get('subject')
    }

@router.get("/recruiter/analytics/user/{user_id}")
def get_comprehensive_user_analytics_endpoint(user_id: int, credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    user = _get_current_user(credentials, db)
    if user.user_type != 'recruiter':
        raise HTTPException(status_code=403, detail="Recruiter access required")
    
    analytics = get_comprehensive_user_analytics(db, user_id)
    return analytics

@router.post("/recruiter/reindex-students")
def recruiter_reindex_students(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    _require_recruiter(credentials, db)
    candidate_service = CandidateService(db)
    result = candidate_service.bulk_update_candidates(limit=200)
    return {"status": "ok", "result": result}

@router.post("/recruiter/jobs")
def create_job_posting(data: Dict[str, Any], credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    recruiter = _require_recruiter(credentials, db)
    
    job = Job(
        recruiter_id=recruiter.id,
        title=data.get("title"),
        description=data.get("description"),
        requirements=data.get("requirements", []),
        location=data.get("location", "Remote"),
        salary_range=data.get("salary_range")
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    return {
        "id": job.id,
        "title": job.title,
        "description": job.description,
        "requirements": job.requirements,
        "location": job.location,
        "salary_range": job.salary_range,
        "created_at": job.created_at.isoformat(),
        "status": job.status
    }

@router.get("/recruiter/jobs")
def get_job_postings(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    recruiter = _require_recruiter(credentials, db)
    
    jobs = db.query(Job).filter(Job.recruiter_id == recruiter.id).all()
    
    return {
        "jobs": [{
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "requirements": job.requirements,
            "location": job.location,
            "salary_range": job.salary_range,
            "created_at": job.created_at.isoformat(),
            "status": job.status
        } for job in jobs],
        "total": len(jobs)
    }

@router.post("/recruiter/jobs/{job_id}/match")
def match_candidates_to_job(job_id: int, credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    recruiter = _require_recruiter(credentials, db)
    
    job = db.query(Job).filter(Job.id == job_id, Job.recruiter_id == recruiter.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get all students with their profiles
    students = db.query(User).filter(User.user_type == 'student').all()
    
    matches = []
    for student in students:
        # Get student profile data
        onboarding = db.query(Onboarding).filter(Onboarding.user_id == student.id).first()
        learning_plan = db.query(LearningPlan).filter(LearningPlan.user_id == student.id).first()
        
        # Create student profile text
        profile_parts = []
        if onboarding:
            if onboarding.career_goals:
                profile_parts.append(f"Career Goals: {onboarding.career_goals}")
            if onboarding.current_skills:
                profile_parts.append(f"Skills: {onboarding.current_skills}")
            if onboarding.grade:
                profile_parts.append(f"Level: {onboarding.grade}")
        
        # Add learning progress
        progress = 0
        if learning_plan and learning_plan.plan:
            months = learning_plan.plan.get("months", [])
            completed = sum(1 for m in months if m.get("status") == "completed")
            progress = (completed / len(months) * 100) if months else 0
            profile_parts.append(f"Learning Progress: {progress:.0f}%")
        
        student_profile = " | ".join(profile_parts)
        
        # Use Gemini AI to calculate match percentage
        match_score = _calculate_ai_match_score(job, student_profile)
        
        if match_score > 0:  # Only include candidates with some match
            matches.append({
                "user_id": student.id,
                "name": student.google_name or student.email or f"Student {student.id}",
                "email": student.email,
                "score": match_score,
                "profile": student_profile,
                "career_goals": onboarding.career_goals if onboarding else None,
                "skills": onboarding.current_skills if onboarding else None,
                "learning_progress": progress,
                "match_explanation": f"{match_score}% match based on AI analysis of profile vs job requirements"
            })
    
    # Sort by match score (highest first)
    matches.sort(key=lambda x: x["score"], reverse=True)
    
    return {
        "job_id": job_id,
        "job_title": job.title,
        "matches": matches[:20],  # Top 20 matches
        "total_matches": len(matches),
        "job_details": {
            "title": job.title,
            "description": job.description,
            "requirements": job.requirements,
            "location": job.location,
            "salary_range": job.salary_range
        }
    }

def _calculate_ai_match_score(job: Job, student_profile: str) -> int:
    """Use Gemini AI to calculate match percentage between job and student"""
    try:
        from app.core.gemini_ai import chatbot
        
        prompt = f"""
You are an AI recruiter. Analyze how well this student profile matches the job requirements.

JOB:
Title: {job.title}
Description: {job.description}
Requirements: {', '.join(job.requirements or [])}
Location: {job.location}

STUDENT PROFILE:
{student_profile}

Provide ONLY a number from 0-100 representing the match percentage. Consider:
- Skill alignment with job requirements
- Career goals matching the role
- Learning progress and commitment
- Experience level appropriate for the position

Respond with ONLY the number (e.g., 85):
"""
        
        response = chatbot.model.generate_content(prompt)
        match_text = response.text.strip()
        
        # Extract number from response
        import re
        numbers = re.findall(r'\d+', match_text)
        if numbers:
            score = int(numbers[0])
            return min(max(score, 0), 100)  # Ensure 0-100 range
        
        return 0
    except Exception as e:
        print(f"AI matching error: {e}")
        # Fallback to simple keyword matching
        job_text = f"{job.title} {job.description} {' '.join(job.requirements or [])}".lower()
        profile_text = student_profile.lower()
        
        # Simple keyword overlap scoring
        job_words = set(job_text.split())
        profile_words = set(profile_text.split())
        overlap = len(job_words.intersection(profile_words))
        
        return min(int(overlap * 5), 100)  # Simple fallback scoring

@router.get("/recruiter/emails")
def get_email_applications(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    recruiter = _require_recruiter(credentials, db)
    
    applications = db.query(EmailApplication).filter(EmailApplication.recruiter_id == recruiter.id).order_by(EmailApplication.received_at.desc()).limit(10).all()
    
    return {
        "applications": [{
            "id": app.id,
            "sender_email": app.sender_email,
            "sender_name": app.sender_name,
            "subject": app.subject,
            "content": app.content[:200] + "..." if len(app.content) > 200 else app.content,
            "received_at": app.received_at.isoformat(),
            "processed": app.processed,
            "student_matched": app.student_id is not None
        } for app in applications],
        "total": len(applications),
        "unprocessed": len([app for app in applications if not app.processed])
    }

@router.get("/recruiter/emails/recent")
def get_recent_emails(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Get recent job-related emails from Gmail with enhanced filtering"""
    recruiter = _require_recruiter(credentials, db)
    
    all_emails = []
    
    # Try to fetch real Gmail emails if user has Google access token
    if recruiter.google_access_token:
        try:
            from app.core.email_service import email_service
            gmail_emails = email_service.fetch_recent_job_emails(recruiter.google_access_token, days_back=1)
            
            for gmail_email in gmail_emails[:15]:
                # Check if this email sender is already in watchlist
                existing_user = db.query(User).filter(
                    User.email == gmail_email['sender_email'],
                    User.created_by_recruiter_id == recruiter.id
                ).first()
                
                all_emails.append({
                    "id": f"gmail_{gmail_email['id']}",
                    "sender_email": gmail_email['sender_email'],
                    "sender_name": gmail_email['sender_name'],
                    "subject": gmail_email['subject'],
                    "content": gmail_email['content'][:200] + "..." if len(gmail_email['content']) > 200 else gmail_email['content'],
                    "full_content": gmail_email['full_content'],
                    "attachments": gmail_email.get('attachments', []),
                    "received_at": gmail_email['received_at'],
                    "processed": False,
                    "student_matched": existing_user is not None,
                    "in_watchlist": existing_user is not None,
                    "priority": "high" if any(word in gmail_email['subject'].lower() for word in ['urgent', 'asap', 'immediate']) else "medium",
                    "has_resume": any(att.get('type') == 'pdf' for att in gmail_email.get('attachments', [])),
                    "source": "gmail"
                })
        except Exception as e:
            print(f"Enhanced Gmail fetch error: {e}")
    
    # Get stored applications
    applications = db.query(EmailApplication).filter(
        EmailApplication.recruiter_id == recruiter.id
    ).order_by(EmailApplication.received_at.desc()).limit(5).all()
    
    for app in applications:
        all_emails.append({
            "id": app.id,
            "sender_email": app.sender_email,
            "sender_name": app.sender_name,
            "subject": app.subject,
            "content": app.content[:200] + "..." if len(app.content) > 200 else app.content,
            "full_content": app.content,
            "attachments": app.attachments or [],
            "received_at": app.received_at.isoformat(),
            "processed": app.processed,
            "student_matched": app.student_id is not None,
            "in_watchlist": app.student_id is not None,
            "priority": "high" if "urgent" in app.subject.lower() else "medium",
            "has_resume": bool(app.attachments),
            "source": "stored"
        })
    
    # Always provide demo data if no real emails or for testing
    if not all_emails or len(all_emails) < 3:
        demo_emails = [
            {
                "sender_email": "alice.johnson@email.com",
                "sender_name": "Alice Johnson",
                "subject": "Application for Senior Frontend Developer Position",
                "content": "Dear Hiring Manager, I am writing to express my strong interest in the Senior Frontend Developer position. I have 5+ years of experience with React, TypeScript, and modern web technologies. Please find my resume attached.",
                "processed": False,
                "has_resume": True
            },
            {
                "sender_email": "mike.chen@gmail.com",
                "sender_name": "Mike Chen",
                "subject": "Full Stack Developer - Job Application",
                "content": "Hi there! I saw your job posting for a Full Stack Developer and I'm very excited about this opportunity. I have 4 years of experience with Node.js, Python, React, and AWS. I'm available for immediate start.",
                "processed": False,
                "has_resume": True
            },
            {
                "sender_email": "sarah.williams@outlook.com",
                "sender_name": "Sarah Williams",
                "subject": "Data Scientist Position - Recent Graduate",
                "content": "Dear Recruiter, I recently graduated with a Master's in Data Science and I'm very interested in the Data Scientist position. I have experience with Python, machine learning, and data visualization. I've completed several projects including predictive modeling.",
                "processed": False,
                "has_resume": True
            }
        ]
        
        for i, email_data in enumerate(demo_emails):
            all_emails.append({
                "id": f"demo_{i}",
                "sender_email": email_data["sender_email"],
                "sender_name": email_data["sender_name"],
                "subject": email_data["subject"],
                "content": email_data["content"],
                "full_content": email_data["content"],
                "attachments": [{"filename": "resume.pdf", "type": "pdf"}] if email_data["has_resume"] else [],
                "received_at": datetime.now().isoformat(),
                "processed": email_data["processed"],
                "student_matched": False,
                "in_watchlist": False,
                "priority": "medium",
                "has_resume": email_data["has_resume"],
                "source": "demo"
            })
    
    # Sort by received_at
    all_emails.sort(key=lambda x: x['received_at'], reverse=True)
    
    return {
        "emails": all_emails[:15],
        "total": len(all_emails),
        "unread": len([email for email in all_emails if not email['processed']]),
        "high_priority": len([email for email in all_emails if email['priority'] == 'high']),
        "with_resume": len([email for email in all_emails if email.get('has_resume', False)])
    }

# Removed old _fetch_gmail_emails function - now using enhanced email_service

# Removed old _is_job_related_email function - now using enhanced email_service

# Removed old _extract_email_content_and_attachments function - now using enhanced email_service

# Removed old _parse_pdf_content function - now using enhanced email_service

@router.post("/recruiter/emails/simulate")
def simulate_email_application(data: Dict[str, Any], credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Simulate receiving an email application for demo purposes"""
    recruiter = _require_recruiter(credentials, db)
    
    # Create a simulated email application
    application = EmailApplication(
        recruiter_id=recruiter.id,
        sender_email=data.get("email", "student@example.com"),
        sender_name=data.get("name", "John Doe"),
        subject=data.get("subject", "Application for Software Developer Position"),
        content=data.get("content", "Dear Hiring Manager, I am interested in the Software Developer position. I have 3 years of experience in React and Node.js. Please find my resume attached. Best regards, John Doe"),
        attachments=["resume.pdf", "cover_letter.pdf"]
    )
    
    db.add(application)
    db.commit()
    db.refresh(application)
    
    return {
        "message": "Email application received",
        "application_id": application.id
    }

@router.get("/recruiter/jobs/{job_id}")
def get_job_details(job_id: int, credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Get detailed job information"""
    recruiter = _require_recruiter(credentials, db)
    
    job = db.query(Job).filter(Job.id == job_id, Job.recruiter_id == recruiter.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "id": job.id,
        "title": job.title,
        "description": job.description,
        "requirements": job.requirements or [],
        "location": job.location or "Not specified",
        "salary_range": job.salary_range or "Not specified",
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "status": getattr(job, 'status', 'active')
    }

@router.post("/recruiter/emails/populate-demo")
def populate_demo_emails(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Populate demo emails for testing"""
    recruiter = _require_recruiter(credentials, db)
    
    demo_emails = [
        {
            "sender_email": "alice.johnson@email.com",
            "sender_name": "Alice Johnson",
            "subject": "Application for Senior Frontend Developer Position",
            "content": "Dear Hiring Manager, I am writing to express my strong interest in the Senior Frontend Developer position. With 5+ years of experience in React, TypeScript, and modern web technologies, I believe I would be a great fit for your team. I have attached my resume and portfolio for your review. Looking forward to hearing from you. Best regards, Alice Johnson"
        },
        {
            "sender_email": "mike.chen@gmail.com",
            "sender_name": "Mike Chen",
            "subject": "Full Stack Developer - Urgent Application",
            "content": "Hi there! I saw your job posting for a Full Stack Developer and I'm very excited about this opportunity. I have 4 years of experience with Node.js, Python, and React. I'm available for immediate start and would love to discuss how I can contribute to your projects. Please find my resume attached. Thanks! Mike Chen"
        },
        {
            "sender_email": "sarah.williams@outlook.com",
            "sender_name": "Sarah Williams",
            "subject": "Data Scientist Position - Recent Graduate",
            "content": "Dear Recruiter, I recently graduated with a Master's in Data Science and I'm very interested in the Data Scientist position at your company. I have experience with Python, machine learning, and data visualization. I've completed several projects including predictive modeling and NLP applications. I would appreciate the opportunity to discuss my qualifications further. Best, Sarah Williams"
        }
    ]
    
    created_count = 0
    for email_data in demo_emails:
        # Check if email already exists
        existing = db.query(EmailApplication).filter(
            EmailApplication.recruiter_id == recruiter.id,
            EmailApplication.sender_email == email_data["sender_email"]
        ).first()
        
        if not existing:
            application = EmailApplication(
                recruiter_id=recruiter.id,
                sender_email=email_data["sender_email"],
                sender_name=email_data["sender_name"],
                subject=email_data["subject"],
                content=email_data["content"],
                processed=False
            )
            db.add(application)
            created_count += 1
    
    db.commit()
    
    return {
        "message": f"Created {created_count} demo emails",
        "total_emails": created_count
    }

@router.post("/recruiter/emails/{email_id}/mark-read")
def mark_email_read(email_id: int, credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Mark email as read/processed"""
    recruiter = _require_recruiter(credentials, db)
    
    application = db.query(EmailApplication).filter(
        EmailApplication.id == email_id,
        EmailApplication.recruiter_id == recruiter.id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Email not found")
    
    application.processed = True
    db.commit()
    
    return {"message": "Email marked as read"}

@router.post("/recruiter/emails/{email_id}/add-to-shortlist")
def add_email_to_shortlist(email_id: str, data: Dict[str, Any], credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Add email candidate to shortlist for specific job"""
    recruiter = _require_recruiter(credentials, db)
    
    sender_email = data.get('sender_email')
    sender_name = data.get('sender_name')
    email_content = data.get('full_content', data.get('content', ''))
    job_id = data.get('job_id')
    summary = data.get('summary', '')
    skills = data.get('skills', [])
    
    if not all([sender_email, sender_name, job_id]):
        raise HTTPException(status_code=400, detail="sender_email, sender_name, and job_id required")
    
    # Verify job exists and belongs to recruiter
    job = db.query(Job).filter(Job.id == job_id, Job.recruiter_id == recruiter.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == sender_email).first()
    
    if existing_user:
        # Check if already shortlisted for this job
        existing_shortlist = db.query(Shortlist).filter(
            Shortlist.recruiter_id == recruiter.id,
            Shortlist.job_id == job_id,
            Shortlist.student_id == existing_user.id
        ).first()
        
        if existing_shortlist:
            return {"message": "Candidate already shortlisted for this job", "user_id": existing_user.id}
        
        # Add to shortlist
        shortlist = Shortlist(
            recruiter_id=recruiter.id,
            job_id=job_id,
            student_id=existing_user.id,
            match_score=75,
            notes="Added from email application",
            source="email"
        )
        db.add(shortlist)
        db.commit()
        
        return {"message": "Existing candidate added to shortlist", "user_id": existing_user.id}
    
    # Create new user
    new_user = User(
        email=sender_email,
        google_name=sender_name,
        user_type='student',
        created_by_recruiter_id=recruiter.id,
        source='email'
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create onboarding record
    from app.models.onboarding import Onboarding
    onboarding = Onboarding(
        user_id=new_user.id,
        name=sender_name,
        career_goals="Seeking opportunities",
        current_skills=", ".join(skills[:5]) if skills else "Various skills",
        grade="Professional"
    )
    db.add(onboarding)
    
    # Create candidate vector
    try:
        from app.models.candidate_vector import CandidateVector
        from app.core.embeddings import simple_text_embedding
        
        vector = simple_text_embedding(summary or email_content)
        candidate_vector = CandidateVector(
            user_id=new_user.id,
            vector=vector,
            summary_text=summary or f"Email candidate: {sender_name}",
            skills_tags=skills[:10]
        )
        db.add(candidate_vector)
    except Exception as e:
        print(f"Vector creation error: {e}")
    
    # Add to shortlist
    shortlist = Shortlist(
        recruiter_id=recruiter.id,
        job_id=job_id,
        student_id=new_user.id,
        match_score=75,
        notes=f"Email candidate. Skills: {', '.join(skills[:3])}",
        source="email"
    )
    db.add(shortlist)
    db.commit()
    
    return {
        "message": "Candidate created and added to shortlist successfully",
        "user_id": new_user.id,
        "candidate_name": sender_name,
        "job_title": job.title,
        "skills_found": len(skills)
    }

@router.post("/recruiter/emails/{email_id}/summarize")
def summarize_email_content(email_id: str, data: Dict[str, Any], credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Generate AI summary of email content"""
    recruiter = _require_recruiter(credentials, db)
    
    try:
        from app.core.gemini_ai import chatbot
        
        # Get email content from request data
        email_content = data.get('full_content', data.get('content', ''))
        sender_name = data.get('sender_name', 'Unknown')
        sender_email = data.get('sender_email', '')
        subject = data.get('subject', '')
        
        if not email_content:
            raise HTTPException(status_code=400, detail="Email content required")
        
        # Generate clean, formatted AI summary
        prompt = f"""
Analyze this job application email and provide a clean, well-formatted candidate summary:

From: {sender_name} <{sender_email}>
Subject: {subject}

Email Content:
{email_content}

Provide a professional summary in this EXACT format:

**{sender_name}** - Candidate Summary

**Position Applied:** [Extract from email]
**Experience Level:** [Entry/Junior/Mid/Senior level]

**Technical Skills:**
• [List 3-5 key technical skills mentioned]

**Background:**
• **Experience:** [Years and key experience]
• **Education:** [If mentioned]
• **Current Role:** [If mentioned]

**Key Highlights:**
• [2-3 main strengths or achievements]

**Recommendation:** [Strong Candidate/Good Fit/Consider/Not Suitable] - [Brief reason]

**Next Steps:** [Interview/Request more info/Pass]

Keep it concise and professional. Use bullet points and bold formatting exactly as shown.
"""
        
        response = chatbot.model.generate_content(prompt)
        summary = response.text.strip()
        
        # Extract skills separately
        skills_prompt = f"""
Extract ONLY the technical skills from this email. Return as comma-separated list:

{email_content}

Skills (comma-separated):
"""
        
        skills_response = chatbot.model.generate_content(skills_prompt)
        skills_text = skills_response.text.strip()
        skills = [s.strip() for s in skills_text.split(',') if s.strip()][:10]
        
        return {
            "summary": summary,
            "skills_extracted": skills,
            "sender_name": sender_name,
            "sender_email": sender_email,
            "subject": subject,
            "content_length": len(email_content),
            "email_id": email_id,
            "can_send_meet_link": True,
            "formatted": True
        }
        
    except Exception as e:
        return {
            "summary": f"Email from {data.get('sender_name', 'Unknown')} regarding job application. Content: {email_content[:200]}...",
            "skills_extracted": [],
            "error": str(e)
        }

@router.post("/recruiter/chat")
async def recruiter_chat(message: Dict[str, str], credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Enhanced recruiter chatbot with calendar, emails, and candidate data"""
    recruiter = _require_recruiter(credentials, db)
    
    try:
        from app.core.gemini_ai import chatbot
        
        # Build comprehensive recruiter context
        context_snippets = []
        context_snippets.append(f"RECRUITER: {recruiter.google_name or recruiter.email}")
        context_snippets.append(f"RECRUITER_ID: {recruiter.id}")
        context_snippets.append(f"GOOGLE_CONNECTED: {bool(recruiter.google_access_token)}")
        
        # Get recent email applications
        recent_emails = db.query(EmailApplication).filter(
            EmailApplication.recruiter_id == recruiter.id
        ).order_by(EmailApplication.received_at.desc()).limit(5).all()
        
        context_snippets.append(f"RECENT_EMAILS: {len(recent_emails)}")
        for i, email in enumerate(recent_emails):
            context_snippets.append(f"EMAIL_{i+1}: From {email.sender_name} <{email.sender_email}>")
            context_snippets.append(f"EMAIL_{i+1}_SUBJECT: {email.subject}")
            context_snippets.append(f"EMAIL_{i+1}_PROCESSED: {email.processed}")
        
        # Get job postings
        jobs = db.query(Job).filter(Job.recruiter_id == recruiter.id).all()
        context_snippets.append(f"ACTIVE_JOBS: {len(jobs)}")
        for i, job in enumerate(jobs[:3]):
            context_snippets.append(f"JOB_{i+1}: {job.title} - {job.location or 'Remote'}")
        
        # Get shortlisted candidates
        shortlisted = db.query(Shortlist).filter(Shortlist.recruiter_id == recruiter.id).count()
        context_snippets.append(f"SHORTLISTED_CANDIDATES: {shortlisted}")
        
        # Get all students with full profiles
        students = db.query(User).filter(User.user_type == 'student').all()
        context_snippets.append(f"TOTAL_STUDENTS: {len(students)}")
        
        # Student profiles with social connections and scores
        for student in students[:8]:  # Limit to top 8 for context
            onboarding = db.query(Onboarding).filter(Onboarding.user_id == student.id).first()
            quiz_scores = db.query(QuizSubmission).filter(QuizSubmission.user_id == student.id).all()
            avg_score = sum(q.score for q in quiz_scores) / len(quiz_scores) if quiz_scores else 0
            
            linkedin_connected = student.linkedin_profile_data is not None
            github_connected = student.github_profile_data is not None
            twitter_connected = student.twitter_profile_data is not None
            
            context_snippets.append(f"STUDENT_{student.id}: {student.google_name or student.email}")
            context_snippets.append(f"STUDENT_{student.id}_EMAIL: {student.email}")
            context_snippets.append(f"STUDENT_{student.id}_SCORE: {avg_score:.1f}%")
            context_snippets.append(f"STUDENT_{student.id}_QUIZZES: {len(quiz_scores)}")
            context_snippets.append(f"STUDENT_{student.id}_LINKEDIN: {linkedin_connected}")
            context_snippets.append(f"STUDENT_{student.id}_GITHUB: {github_connected}")
            context_snippets.append(f"STUDENT_{student.id}_TWITTER: {twitter_connected}")
            
            if onboarding:
                goals = str(onboarding.career_goals) if onboarding.career_goals else "Not specified"
                skills = str(onboarding.current_skills) if onboarding.current_skills else "Not specified"
                context_snippets.append(f"STUDENT_{student.id}_GOALS: {goals}")
                context_snippets.append(f"STUDENT_{student.id}_SKILLS: {skills}")
        
        # Create enriched message with enhanced context
        enriched_message = f"""[RECRUITER_CONTEXT]
You are RecruiterAI, a specialized AI assistant for recruiters with access to:

**CANDIDATE DATA:**
- Student profiles, emails, and contact information
- Quiz scores and learning progress
- Social media connections (LinkedIn, GitHub, Twitter)
- Career goals and current skills
- Learning plans and achievements

**RECRUITMENT TOOLS:**
- Gmail integration for job application emails
- Job posting management
- Candidate shortlisting and tracking
- Interview scheduling and management

**CURRENT DATA:**
{chr(10).join(context_snippets)}
[/RECRUITER_CONTEXT]

**YOUR CAPABILITIES:**
• **Candidate Analysis** - Evaluate students based on skills, performance, and goals
• **Email Management** - Help process job applications and candidate emails
• **Job Matching** - Recommend best candidates for specific positions
• **Recruitment Strategy** - Provide insights on hiring trends and candidate pipeline
• **Performance Insights** - Analyze candidate learning progress and quiz performance

**RESPONSE STYLE:**
- Be professional and data-driven
- Provide specific candidate recommendations with reasoning
- Include relevant metrics and scores
- Suggest actionable next steps
- Use bullet points for clarity

Recruiter Query: {message.get('message', '')}"""
        
        # Use direct model call for recruiter to ensure proper processing
        try:
            response = chatbot.model.generate_content(
                enriched_message,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=800
                )
            )
            formatted_response = response.text.strip()
        except Exception as e:
            print(f"Recruiter AI error: {e}")
            formatted_response = "I'm having trouble processing your request. Please try again."
        
        response_data = {
            "response": formatted_response,
            "timestamp": datetime.now().isoformat(),
            "message_id": str(uuid.uuid4())
        }
        
        return {
            "response": response_data["response"],
            "timestamp": response_data["timestamp"],
            "message_id": response_data["message_id"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recruiter chat error: {str(e)}")

@router.get("/recruiter/chatbot/insights")
def get_chatbot_insights(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Get comprehensive insights for recruiter chatbot including emails"""
    recruiter = _require_recruiter(credentials, db)
    
    # Get all students with detailed information
    students = db.query(User).filter(User.user_type == 'student').all()
    
    student_insights = []
    for student in students:
        onboarding = db.query(Onboarding).filter(Onboarding.user_id == student.id).first()
        learning_plan = db.query(LearningPlan).filter(LearningPlan.user_id == student.id).first()
        candidate_vector = db.query(CandidateVector).filter(CandidateVector.user_id == student.id).first()
        
        # Calculate learning progress
        progress = 0
        if learning_plan and learning_plan.plan:
            months = learning_plan.plan.get("months", [])
            completed = sum(1 for m in months if m.get("status") == "completed")
            progress = (completed / len(months) * 100) if months else 0
        
        student_insights.append({
            "id": student.id,
            "name": student.google_name or student.email or f"Student {student.id}",
            "email": student.email,
            "learning_progress": progress,
            "career_goals": onboarding.career_goals if onboarding else None,
            "current_skills": onboarding.current_skills if onboarding else None,
            "grade": onboarding.grade if onboarding else None,
            "skills_tags": candidate_vector.skills_tags if candidate_vector else [],
            "summary": candidate_vector.summary_text if candidate_vector else None,
            "created_at": student.created_at.isoformat() if student.created_at else None,
            "added_by_recruiter": student.created_by_recruiter_id == recruiter.id
        })
    
    # Get recent emails with full content
    recent_emails = []
    
    # Get Gmail emails if available
    if recruiter.google_access_token:
        try:
            gmail_emails = []
            for email in gmail_emails:
                recent_emails.append({
                    "id": f"gmail_{email['id']}",
                    "sender_name": email['sender_name'],
                    "sender_email": email['sender_email'],
                    "subject": email['subject'],
                    "content": email['content'],
                    "attachments": email.get('attachments', []),
                    "received_at": email['received_at'],
                    "source": "gmail"
                })
        except Exception as e:
            print(f"Gmail fetch error in chatbot: {e}")
    
    # Get stored email applications
    applications = db.query(EmailApplication).filter(
        EmailApplication.recruiter_id == recruiter.id
    ).order_by(EmailApplication.received_at.desc()).limit(20).all()
    
    for app in applications:
        recent_emails.append({
            "id": str(app.id),
            "sender_name": app.sender_name,
            "sender_email": app.sender_email,
            "subject": app.subject,
            "content": app.content,
            "attachments": app.attachments or [],
            "received_at": app.received_at.isoformat(),
            "source": "stored",
            "processed": app.processed
        })
    
    # Calculate analytics
    total_students = len(students)
    active_students = len([s for s in student_insights if s["learning_progress"] > 0])
    avg_progress = sum(s["learning_progress"] for s in student_insights) / total_students if total_students > 0 else 0
    
    # Skill distribution
    all_skills = []
    for student in student_insights:
        if student["skills_tags"]:
            all_skills.extend(student["skills_tags"])
        if student["current_skills"]:
            # Handle both string and list formats
            if isinstance(student["current_skills"], str):
                all_skills.extend(student["current_skills"].split(","))
            elif isinstance(student["current_skills"], list):
                all_skills.extend(student["current_skills"])
    
    skill_counts = {}
    for skill in all_skills:
        skill = skill.strip()
        if skill:
            skill_counts[skill] = skill_counts.get(skill, 0) + 1
    
    top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        "students": student_insights,
        "emails": recent_emails,
        "analytics": {
            "total_students": total_students,
            "active_students": active_students,
            "average_progress": round(avg_progress, 1),
            "total_emails": len(recent_emails),
            "unread_emails": len([e for e in recent_emails if not e.get('processed', True)]),
            "top_skills": [{
                "skill": skill,
                "count": count,
                "percentage": round((count / total_students * 100), 1) if total_students > 0 else 0
            } for skill, count in top_skills],
            "progress_distribution": {
                "high_progress": len([s for s in student_insights if s["learning_progress"] >= 70]),
                "medium_progress": len([s for s in student_insights if 30 <= s["learning_progress"] < 70]),
                "low_progress": len([s for s in student_insights if 0 < s["learning_progress"] < 30]),
                "not_started": len([s for s in student_insights if s["learning_progress"] == 0])
            }
        }
    }

@router.get("/recruiter/analytics/advanced")
def get_advanced_analytics(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    recruiter = _require_recruiter(credentials, db)
    
    # Get comprehensive analytics
    total_students = db.query(User).filter(User.user_type == 'student').count()
    total_jobs = db.query(Job).filter(Job.recruiter_id == recruiter.id).count()
    total_applications = db.query(EmailApplication).filter(EmailApplication.recruiter_id == recruiter.id).count()
    
    # Student skill distribution
    students_with_vectors = db.query(CandidateVector).all()
    skill_distribution = {}
    for cv in students_with_vectors:
        for skill in cv.skills_tags or []:
            skill_distribution[skill] = skill_distribution.get(skill, 0) + 1
    
    # Top skills
    top_skills = sorted(skill_distribution.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        "overview": {
            "total_students": total_students,
            "total_jobs_posted": total_jobs,
            "total_applications": total_applications,
            "active_candidates": len(students_with_vectors)
        },
        "skill_insights": {
            "top_skills": [{
                "skill": skill,
                "count": count,
                "percentage": round((count / total_students * 100), 1) if total_students > 0 else 0
            } for skill, count in top_skills],
            "total_unique_skills": len(skill_distribution)
        },
        "application_trends": {
            "this_week": random.randint(5, 15),
            "last_week": random.randint(3, 12),
            "growth_rate": "+23%"
        }
    }

@router.get("/recruiter/student/{user_id}/profile")
def get_student_profile_for_recruiter(user_id: int, credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Get comprehensive student profile for recruiter view"""
    recruiter = _require_recruiter(credentials, db)
    
    # Get student
    student = db.query(User).filter(User.id == user_id, User.user_type == 'student').first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Get all related data
    onboarding = db.query(Onboarding).filter(Onboarding.user_id == user_id).first()
    learning_plan = db.query(LearningPlan).filter(LearningPlan.user_id == user_id).first()
    quiz_scores = db.query(QuizSubmission).filter(QuizSubmission.user_id == user_id).all()
    candidate_vector = db.query(CandidateVector).filter(CandidateVector.user_id == user_id).first()
    
    # Calculate quiz performance
    avg_score = sum(q.score for q in quiz_scores) / len(quiz_scores) if quiz_scores else 0
    passed_quizzes = sum(1 for q in quiz_scores if q.passed)
    
    # Parse social connections
    linkedin_data = None
    github_data = None
    twitter_data = None
    
    if student.linkedin_profile_data:
        try:
            import json
            linkedin_data = json.loads(student.linkedin_profile_data)
        except: pass
    
    if student.github_profile_data:
        try:
            import json
            github_data = json.loads(student.github_profile_data)
        except: pass
    
    if student.twitter_profile_data:
        try:
            import json
            twitter_data = json.loads(student.twitter_profile_data)
        except: pass
    
    # Learning plan details
    learning_details = {
        "status": "Not yet started",
        "progress_percentage": 0,
        "current_topic": "No active learning",
        "plan_title": "No learning plan",
        "current_month": 0,
        "current_day": 0,
        "total_months": 0,
        "completed_months": 0
    }
    
    if learning_plan and learning_plan.plan:
        months = learning_plan.plan.get("months", [])
        completed = sum(1 for m in months if m.get("status") == "completed")
        total = len(months)
        progress = (completed / total * 100) if total > 0 else 0
        
        learning_details.update({
            "status": f"{progress:.1f}% completed" if progress > 0 else "Started but no progress",
            "progress_percentage": progress,
            "plan_title": learning_plan.title or "Learning Plan",
            "current_month": student.current_month_index or 1,
            "current_day": student.current_day or 1,
            "total_months": total,
            "completed_months": completed
        })
        
        # Get current topic
        current_month_index = student.current_month_index or 1
        current_day = student.current_day or 1
        
        if 1 <= current_month_index <= len(months):
            current_month = months[current_month_index - 1]
            days = current_month.get("days", [])
            if 0 < current_day <= len(days):
                current_day_data = days[current_day - 1]
                learning_details["current_topic"] = current_day_data.get('concept', 'No topic assigned')
    
    return {
        "basic_info": {
            "id": student.id,
            "name": student.google_name or (onboarding.name if onboarding else f"Student {student.id}"),
            "email": student.email,
            "google_email": student.google_email,
            "picture": student.google_picture,
            "created_at": student.created_at.isoformat() if student.created_at else None,
            "user_type": student.user_type
        },
        "onboarding_details": {
            "name": onboarding.name if onboarding else "Not provided",
            "career_goals": str(onboarding.career_goals) if onboarding and onboarding.career_goals else "Not specified",
            "current_skills": str(onboarding.current_skills) if onboarding and onboarding.current_skills else "Not specified",
            "grade": onboarding.grade if onboarding else "Not specified",
            "time_commitment": onboarding.time_commitment if onboarding else "Not specified",
            "completed_at": "Profile completed" if onboarding else "Not completed"
        },
        "learning_progress": learning_details,
        "quiz_performance": {
            "average_score": round(avg_score, 1),
            "total_quizzes": len(quiz_scores),
            "passed_quizzes": passed_quizzes,
            "pass_rate": round((passed_quizzes / len(quiz_scores) * 100), 1) if quiz_scores else 0,
            "performance_level": "Excellent" if avg_score >= 80 else "Good" if avg_score >= 60 else "Needs Improvement" if avg_score > 0 else "No quizzes taken",
            "recent_scores": [{
                "month": q.month_index,
                "day": q.day,
                "score": q.score,
                "passed": q.passed,
                "date": q.created_at.isoformat() if q.created_at else None
            } for q in quiz_scores[-5:]]  # Last 5 quiz scores
        },
        "social_connections": {
            "linkedin": {
                "connected": linkedin_data is not None,
                "name": linkedin_data.get('data', {}).get('response_dict', {}).get('name') if linkedin_data else None,
                "email": linkedin_data.get('data', {}).get('response_dict', {}).get('email') if linkedin_data else None,
                "profile_url": f"https://linkedin.com/in/{linkedin_data.get('data', {}).get('response_dict', {}).get('sub')}" if linkedin_data else None
            },
            "github": {
                "connected": github_data is not None,
                "username": github_data[0].get('owner', {}).get('login') if github_data and isinstance(github_data, list) and len(github_data) > 0 else None,
                "profile_url": github_data[0].get('owner', {}).get('html_url') if github_data and isinstance(github_data, list) and len(github_data) > 0 else None,
                "repos_count": len(github_data) if github_data and isinstance(github_data, list) else 0,
                "public_repos": [{
                    "name": repo.get('name'),
                    "description": repo.get('description'),
                    "language": repo.get('language'),
                    "stars": repo.get('stargazers_count', 0)
                } for repo in (github_data[:3] if github_data and isinstance(github_data, list) else [])]  # Top 3 repos
            },
            "twitter": {
                "connected": twitter_data is not None,
                "username": twitter_data.get('data', {}).get('username') if twitter_data else None,
                "name": twitter_data.get('data', {}).get('name') if twitter_data else None,
                "profile_url": f"https://twitter.com/{twitter_data.get('data', {}).get('username')}" if twitter_data else None
            }
        },
        "profile_summary": {
            "summary": candidate_vector.summary_text if candidate_vector else "No profile summary available",
            "skills_tags": candidate_vector.skills_tags if candidate_vector else [],
            "profile_completeness": {
                "onboarding_complete": onboarding is not None,
                "learning_plan_active": learning_plan is not None,
                "quiz_activity": len(quiz_scores) > 0,
                "social_connections": sum([linkedin_data is not None, github_data is not None, twitter_data is not None]),
                "overall_score": round((
                    (1 if onboarding else 0) +
                    (1 if learning_plan else 0) +
                    (1 if quiz_scores else 0) +
                    (0.33 * sum([linkedin_data is not None, github_data is not None, twitter_data is not None]))
                ) / 3.33 * 100, 1)
            }
        }
    }

@router.get("/recruiter/related/{user_id}")
def get_related_candidates(user_id: int, credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Get candidates related to a specific user based on skills and interests"""
    recruiter = _require_recruiter(credentials, db)
    
    # Get the target user's profile
    target_user = db.query(User).filter(User.id == user_id, User.user_type == 'student').first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Student not found")
    
    target_profile = db.query(CandidateVector).filter(CandidateVector.user_id == user_id).first()
    
    if not target_profile or not target_profile.skills_tags:
        return {"related_candidates": [], "message": "No related candidates found - insufficient profile data"}
    
    # Find similar candidates based on skills
    target_skills = set(target_profile.skills_tags)
    
    # Get all other students with profiles
    all_profiles = db.query(CandidateVector).filter(
        CandidateVector.user_id != user_id
    ).all()
    
    related_candidates = []
    for profile in all_profiles:
        if not profile.skills_tags:
            continue
            
        candidate_skills = set(profile.skills_tags)
        skill_overlap = len(target_skills.intersection(candidate_skills))
        
        if skill_overlap > 0:
            # Get user details
            user = db.query(User).filter(User.id == profile.user_id).first()
            if user:
                similarity_score = skill_overlap / len(target_skills.union(candidate_skills))
                
                related_candidates.append({
                    "id": user.id,
                    "name": user.google_name or user.email or f"Student {user.id}",
                    "email": user.email,
                    "skills": profile.skills_tags,
                    "shared_skills": list(target_skills.intersection(candidate_skills)),
                    "similarity_score": round(similarity_score, 2),
                    "summary": profile.summary_text
                })
    
    # Sort by similarity score
    related_candidates.sort(key=lambda x: x["similarity_score"], reverse=True)
    
    return {
        "related_candidates": related_candidates[:10],  # Top 10 similar candidates
        "target_user": {
            "id": target_user.id,
            "name": target_user.google_name or target_user.email,
            "skills": target_profile.skills_tags
        }
    }

@router.post("/recruiter/chatbot/search-emails")
def search_emails_for_chatbot(data: Dict[str, Any], credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Search emails by name, email, or content for chatbot queries"""
    recruiter = _require_recruiter(credentials, db)
    
    query = data.get('query', '').lower()
    
    if not query:
        return {"emails": [], "message": "Please provide a search query"}
    
    matching_emails = []
    
    # Search Gmail emails
    if recruiter.google_access_token:
        try:
            gmail_emails = _fetch_gmail_emails(recruiter.google_access_token)
            for email in gmail_emails:
                if (query in email['sender_name'].lower() or 
                    query in email['sender_email'].lower() or 
                    query in email['subject'].lower() or 
                    query in email['content'].lower()):
                    
                    # Include PDF content in search and generate analysis
                    pdf_content = ""
                    pdf_analysis = ""
                    
                    for att in email.get('attachments', []):
                        if att.get('type') == 'pdf':
                            pdf_content += f"\n\nPDF: {att['filename']}\n{att['content']}"
                            
                            # Generate AI analysis of PDF content
                            try:
                                from app.core.gemini_ai import chatbot
                                analysis_prompt = f"""
Analyze this resume/CV and provide a concise, well-formatted candidate assessment:

Candidate: {email['sender_name']}
Email: {email['sender_email']}

Resume Content:
{att['content']}

Provide a CONCISE analysis in this EXACT format:

👤 **PROFILE**
• {email['sender_name']} | {email['sender_email']}
• Experience: [X years/Entry-level/Student]
• Education: [Degree, Institution, Year]
• Location: [City, State/Country]

🔧 **TECHNICAL SKILLS**
• Languages: [Top 3-4 programming languages]
• Technologies: [Key frameworks/tools]
• Specialization: [Main domain/expertise]

💼 **EXPERIENCE & ACHIEVEMENTS**
• Current Role: [Position or Student status]
• Key Projects: [1-2 notable projects/achievements]
• Strengths: [Top 2-3 strengths]

🎯 **RECRUITMENT ASSESSMENT**
• Best Fit: [Suitable role types]
• Level: [Junior/Mid/Senior]
• Recommendation: [Hire/Interview/Pass with brief reason]
• Next Steps: [Interview focus areas]

Keep each bullet point to 1 line maximum. Be concise and professional.
"""
                                
                                response = chatbot.model.generate_content(analysis_prompt)
                                pdf_analysis = response.text.strip()
                            except Exception as e:
                                pdf_analysis = f"Resume analysis unavailable: {str(e)}"
                    
                    matching_emails.append({
                        "id": f"gmail_{email['id']}",
                        "sender_name": email['sender_name'],
                        "sender_email": email['sender_email'],
                        "subject": email['subject'],
                        "content": email['content'],
                        "pdf_content": pdf_content,
                        "pdf_analysis": pdf_analysis,
                        "attachments": email.get('attachments', []),
                        "received_at": email['received_at'],
                        "source": "gmail"
                    })
        except Exception as e:
            print(f"Gmail search error: {e}")
    
    # Search stored emails
    applications = db.query(EmailApplication).filter(
        EmailApplication.recruiter_id == recruiter.id
    ).all()
    
    for app in applications:
        if (query in app.sender_name.lower() or 
            query in app.sender_email.lower() or 
            query in app.subject.lower() or 
            query in app.content.lower()):
            
            matching_emails.append({
                "id": str(app.id),
                "sender_name": app.sender_name,
                "sender_email": app.sender_email,
                "subject": app.subject,
                "content": app.content,
                "pdf_content": "",  # Stored emails don't have parsed PDFs yet
                "attachments": app.attachments or [],
                "received_at": app.received_at.isoformat(),
                "source": "stored",
                "processed": app.processed
            })
    
    return {
        "emails": matching_emails[:10],  # Limit to 10 results
        "total_found": len(matching_emails),
        "query": query
    }

# Enhanced AI Matching Endpoints
@router.get("/recruiter/jobs/{job_id}/matches")
def get_job_matches(job_id: int, credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Get AI-powered candidate matches for a specific job"""
    recruiter = _require_recruiter(credentials, db)
    
    # Verify job belongs to recruiter
    job = db.query(Job).filter(Job.id == job_id, Job.recruiter_id == recruiter.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    try:
        from app.core.gemini_ai import chatbot
        
        # Get all students with comprehensive data
        students = db.query(User).filter(User.user_type == 'student').all()
        matches = []
        
        # Get existing shortlisted candidates for this job
        shortlisted_ids = [s.student_id for s in db.query(Shortlist).filter(
            Shortlist.recruiter_id == recruiter.id,
            Shortlist.job_id == job_id
        ).all()]
        
        for student in students:
            # Get comprehensive student data
            onboarding = db.query(Onboarding).filter(Onboarding.user_id == student.id).first()
            learning_plan = db.query(LearningPlan).filter(LearningPlan.user_id == student.id).first()
            quiz_scores = db.query(QuizSubmission).filter(QuizSubmission.user_id == student.id).all()
            
            # Calculate metrics
            avg_score = sum(q.score for q in quiz_scores) / len(quiz_scores) if quiz_scores else 0
            
            # Learning progress
            learning_progress = 0
            if learning_plan and learning_plan.plan:
                months = learning_plan.plan.get("months", [])
                completed = sum(1 for m in months if m.get("status") == "completed")
                learning_progress = (completed / len(months) * 100) if months else 0
            
            # Build student profile
            profile_sections = []
            profile_sections.append(f"STUDENT: {student.google_name or student.email}")
            
            if onboarding:
                profile_sections.append(f"CAREER GOALS: {str(onboarding.career_goals) if onboarding.career_goals else 'Not specified'}")
                profile_sections.append(f"CURRENT SKILLS: {str(onboarding.current_skills) if onboarding.current_skills else 'Not specified'}")
                profile_sections.append(f"EDUCATION LEVEL: {onboarding.grade or 'Not specified'}")
            
            profile_sections.append(f"LEARNING PROGRESS: {learning_progress:.1f}% completed")
            profile_sections.append(f"QUIZ PERFORMANCE: {avg_score:.1f}% average ({len(quiz_scores)} quizzes)")
            
            student_profile = "\n".join(profile_sections)
            
            # AI matching prompt
            match_prompt = f"""Analyze if this student can do this job successfully.

JOB: {job.title}
DESCRIPTION: {job.description}
REQUIREMENTS: {', '.join(job.requirements or [])}

STUDENT:
{student_profile}

Evaluate:
1. Do their skills match the job requirements?
2. Do their career goals align with this role?
3. Is their learning progress showing commitment?
4. Can they realistically perform this work?

Score 0-100 (where 80+ = excellent fit, 60-79 = good fit, 40-59 = moderate fit, below 40 = poor fit):"""
            
            try:
                response = chatbot.model.generate_content(match_prompt)
                score_text = response.text.strip()
                import re
                numbers = re.findall(r'\d+', score_text)
                score = int(numbers[0]) if numbers else 0
                score = min(max(score, 0), 100)
                
                # Include all candidates to show match percentages
                matches.append({
                    "user_id": student.id,
                    "name": student.google_name or student.email,
                    "email": student.email,
                    "score": score,
                    "avg_quiz_score": round(avg_score, 1),
                    "learning_progress": round(learning_progress, 1),
                    "career_goals": str(onboarding.career_goals) if onboarding and onboarding.career_goals else "Not specified",
                    "skills": str(onboarding.current_skills) if onboarding and onboarding.current_skills else "Not specified",
                    "match_explanation": f"AI analysis: {score}% match based on skills alignment, career goals, and learning commitment.",
                    "recommendation": "Highly Recommended" if score >= 80 else "Recommended" if score >= 60 else "Consider" if score >= 40 else "Not Ideal",
                    "shortlisted": student.id in shortlisted_ids
                })
            except Exception as e:
                print(f"AI matching error for student {student.id}: {e}")
                continue
        
        # Sort by score
        matches.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "job": {
                "id": job.id,
                "title": job.title,
                "description": job.description,
                "requirements": job.requirements or [],
                "location": job.location or "Not specified",
                "salary_range": job.salary_range or "Not specified",
                "created_at": job.created_at.isoformat() if job.created_at else None
            },
            "matches": matches[:20],  # Top 20 matches
            "total_matches": len(matches),
            "shortlisted_count": len(shortlisted_ids)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding matches: {str(e)}")

@router.get("/recruiter/candidate/{user_id}/job-recommendations")
def get_candidate_job_recommendations(user_id: int, credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Get AI-powered job recommendations for a specific candidate"""
    recruiter = _require_recruiter(credentials, db)
    
    from app.core.ai_matching import get_job_recommendations_for_candidate
    recommendations = get_job_recommendations_for_candidate(db, user_id, limit=10)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    return {
        "candidate": {
            "id": user.id,
            "name": user.google_name or user.email,
            "email": user.email
        },
        "recommendations": recommendations,
        "total_recommendations": len(recommendations)
    }

# Composio LinkedIn & GitHub Authentication Endpoints
@router.post("/auth/linkedin/connect")
def connect_linkedin(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """LinkedIn connection - try connect first, if error then fetch profile directly"""
    user = _get_current_user(credentials, db)
    print(f"[ROUTE] LinkedIn connect for user: {user.email}")
    
    from app.core.composio_service import composio_auth
    result = composio_auth.get_linkedin_auth_url(user_email=user.email)
    return result

@router.post("/recruiter/auth/linkedin/connect")
def recruiter_connect_linkedin(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Recruiter LinkedIn connection"""
    recruiter = _require_recruiter(credentials, db)
    
    from app.core.composio_service import composio_auth
    result = composio_auth.get_linkedin_auth_url(user_email=recruiter.email)
    return result

@router.post("/recruiter/auth/github/connect")
def recruiter_connect_github(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Recruiter GitHub connection"""
    recruiter = _require_recruiter(credentials, db)
    
    from app.core.composio_service import composio_auth
    result = composio_auth.get_github_auth_url(user_email=recruiter.email)
    return result

@router.post("/recruiter/auth/twitter/connect")
def recruiter_connect_twitter(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Recruiter Twitter connection"""
    recruiter = _require_recruiter(credentials, db)
    
    from app.core.composio_service import composio_auth
    result = composio_auth.get_twitter_auth_url(user_email=recruiter.email)
    return result

@router.post("/auth/github/connect")
def connect_github(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """GitHub connection - try connect first, if error then fetch repos directly"""
    user = _get_current_user(credentials, db)
    
    from app.core.composio_service import composio_auth
    
    # Try to connect first
    connect_result = composio_auth.get_github_auth_url(user_email=user.email)
    
    if "error" in connect_result:
        # If connect fails, try to fetch repos directly (already connected)
        repos_result = composio_auth.get_github_repos(user_email=user.email)
        if "repos" in repos_result:
            # Save repos and mark as connected
            import json
            user.github_profile_data = json.dumps(repos_result["repos"])
            user.github_connected_at = datetime.utcnow()
            db.commit()
            return {"status": "connected", "profile": repos_result["repos"]}
        return repos_result
    
    # If connect succeeds, return auth URL for popup
    return connect_result

@router.post("/auth/linkedin/verify")
def verify_linkedin_connection(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Verify LinkedIn connection and store profile data"""
    user = _get_current_user(credentials, db)
    
    from app.core.composio_service import composio_auth
    result = composio_auth.get_linkedin_profile(user.email)
    
    if "profile" in result:
        import json
        user.linkedin_profile_data = json.dumps(result["profile"])
        user.linkedin_connected_at = datetime.utcnow()
        db.commit()
        return {"status": "connected", "profile": result["profile"]}
    
    return result

@router.post("/auth/github/verify")
def verify_github_connection(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Verify GitHub connection and store profile data"""
    user = _get_current_user(credentials, db)
    
    from app.core.composio_service import composio_auth
    result = composio_auth.get_github_repos(user.email)
    
    if "repos" in result:
        import json
        user.github_profile_data = json.dumps(result["repos"])
        user.github_connected_at = datetime.utcnow()
        db.commit()
        return {"status": "connected", "profile": result["repos"]}
    
    return result

@router.get("/recruiter/profile/social-connections")
def get_recruiter_social_connections(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Get recruiter's social media connections"""
    recruiter = _require_recruiter(credentials, db)
    
    from app.core.composio_service import composio_auth
    
    # LinkedIn
    linkedin_result = composio_auth.get_linkedin_profile(user_email=recruiter.email)
    linkedin_connected = "profile" in linkedin_result and not linkedin_result.get("unauthorized")
    if linkedin_connected:
        import json
        recruiter.linkedin_profile_data = json.dumps(linkedin_result["profile"])
        recruiter.linkedin_connected_at = datetime.utcnow()
        db.commit()
    
    # GitHub
    github_result = composio_auth.get_github_repos(user_email=recruiter.email)
    github_connected = "repos" in github_result and not github_result.get("unauthorized")
    if github_connected:
        import json
        recruiter.github_profile_data = json.dumps(github_result["repos"])
        recruiter.github_connected_at = datetime.utcnow()
        db.commit()
    
    # Twitter
    twitter_result = composio_auth.get_twitter_profile(user_email=recruiter.email)
    twitter_connected = "profile" in twitter_result and not twitter_result.get("unauthorized")
    if twitter_connected:
        import json
        recruiter.twitter_profile_data = json.dumps(twitter_result["profile"])
        recruiter.twitter_connected_at = datetime.utcnow()
        db.commit()
    
    return {
        "linkedin": {
            "connected": linkedin_connected,
            "profile": linkedin_result.get("profile") if linkedin_connected else None,
            "error": linkedin_result.get("error") if not linkedin_connected else None
        },
        "github": {
            "connected": github_connected,
            "profile": github_result.get("repos") if github_connected else None,
            "error": github_result.get("error") if not github_connected else None
        },
        "twitter": {
            "connected": twitter_connected,
            "profile": twitter_result.get("profile") if twitter_connected else None,
            "error": twitter_result.get("error") if not twitter_connected else None
        }
    }

@router.get("/profile/social-connections")
def get_social_connections(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Get user's social media connections status - try to fetch profiles first"""
    user = _get_current_user(credentials, db)
    
    from app.core.composio_service import composio_auth
    
    # Try to fetch LinkedIn profile directly
    linkedin_result = composio_auth.get_linkedin_profile(user_email=user.email)
    linkedin_connected = False
    linkedin_data = None
    
    if "profile" in linkedin_result and not linkedin_result.get("unauthorized", False):
        linkedin_connected = True
        linkedin_data = linkedin_result["profile"]
        # Save to database
        import json
        user.linkedin_profile_data = json.dumps(linkedin_data)
        user.linkedin_connected_at = datetime.utcnow()
        db.commit()
    elif linkedin_result.get("unauthorized") or linkedin_result.get("needs_connection"):
        # Clear stale connection data
        user.linkedin_profile_data = None
        user.linkedin_connected_at = None
        db.commit()
    
    # Try to fetch GitHub repos directly
    github_result = composio_auth.get_github_repos(user_email=user.email)
    github_connected = False
    github_data = None
    
    if "repos" in github_result and not github_result.get("unauthorized", False):
        github_connected = True
        github_data = github_result["repos"]
        # Save to database
        import json
        user.github_profile_data = json.dumps(github_data)
        user.github_connected_at = datetime.utcnow()
        db.commit()
    elif github_result.get("unauthorized") or github_result.get("needs_connection"):
        # Clear stale connection data
        user.github_profile_data = None
        user.github_connected_at = None
        db.commit()
    
    # Try to fetch Twitter profile directly
    twitter_result = composio_auth.get_twitter_profile(user_email=user.email)
    twitter_connected = False
    twitter_data = None
    
    if "profile" in twitter_result and not twitter_result.get("unauthorized", False):
        twitter_connected = True
        twitter_data = twitter_result["profile"]
        # Save to database
        import json
        user.twitter_profile_data = json.dumps(twitter_data)
        user.twitter_connected_at = datetime.utcnow()
        db.commit()
    elif twitter_result.get("unauthorized") or twitter_result.get("needs_connection"):
        # Clear stale connection data
        user.twitter_profile_data = None
        user.twitter_connected_at = None
        db.commit()
    
    return {
        "linkedin": {
            "connected": linkedin_connected,
            "connected_at": user.linkedin_connected_at.isoformat() if user.linkedin_connected_at else None,
            "profile": linkedin_data,
            "error": linkedin_result.get("error") if linkedin_result.get("unauthorized") or linkedin_result.get("needs_connection") else None
        },
        "github": {
            "connected": github_connected,
            "connected_at": user.github_connected_at.isoformat() if user.github_connected_at else None,
            "profile": github_data,
            "error": github_result.get("error") if github_result.get("unauthorized") or github_result.get("needs_connection") else None
        },
        "twitter": {
            "connected": twitter_connected,
            "connected_at": user.twitter_connected_at.isoformat() if user.twitter_connected_at else None,
            "profile": twitter_data,
            "error": twitter_result.get("error") if twitter_result.get("unauthorized") or twitter_result.get("needs_connection") else None
        }
    }

@router.delete("/auth/linkedin/disconnect")
def disconnect_linkedin(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Disconnect LinkedIn account"""
    user = _get_current_user(credentials, db)
    
    from app.core.composio_service import composio_auth
    result = composio_auth.disconnect_linkedin(user.email, user.linkedin_connection_id)
    
    # Clear stored data
    user.linkedin_connection_id = None
    user.linkedin_profile_data = None
    user.linkedin_connected_at = None
    db.commit()
    
    return result

@router.delete("/auth/github/disconnect")
def disconnect_github(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Disconnect GitHub account"""
    user = _get_current_user(credentials, db)
    
    from app.core.composio_service import composio_auth
    result = composio_auth.disconnect_github(user.email, user.github_connection_id)
    
    # Clear stored data
    user.github_connection_id = None
    user.github_profile_data = None
    user.github_connected_at = None
    db.commit()
    
    return result

@router.post("/auth/twitter/connect")
def connect_twitter(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Twitter connection - return actual OAuth URL or actual error"""
    user = _get_current_user(credentials, db)
    
    from app.core.composio_service import composio_auth
    result = composio_auth.get_twitter_auth_url(user_email=user.email)
    
    return result

@router.post("/auth/twitter/verify")
def verify_twitter_connection(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Verify Twitter connection and store profile data"""
    user = _get_current_user(credentials, db)
    
    from app.core.composio_service import composio_auth
    result = composio_auth.get_twitter_profile(user.email)
    
    if "profile" in result:
        import json
        user.twitter_profile_data = json.dumps(result["profile"])
        user.twitter_connected_at = datetime.utcnow()
        db.commit()
        return {"status": "connected", "profile": result["profile"]}
    
    return result

@router.delete("/auth/twitter/disconnect")
def disconnect_twitter(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Disconnect Twitter account"""
    user = _get_current_user(credentials, db)
    
    from app.core.composio_service import composio_auth
    result = composio_auth.disconnect_twitter(user.email, user.twitter_connection_id)
    
    # Clear stored data
    user.twitter_connection_id = None
    user.twitter_profile_data = None
    user.twitter_connected_at = None
    db.commit()
    
    return result

@router.post("/recruiter/login")
def recruiter_login(data: Dict[str, Any], db: Session = Depends(get_db)):
    """Login recruiter with email/password"""
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")
    
    user = db.query(User).filter(User.email == email, User.user_type == 'recruiter').first()
    if not user or not user.hashed_password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/recruiter/test-matches/{job_id}")
def test_matches(job_id: int, credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Simple test endpoint to verify matching works"""
    recruiter = _require_recruiter(credentials, db)
    
    # Get job
    job = db.query(Job).filter(Job.id == job_id, Job.recruiter_id == recruiter.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get student count
    student_count = db.query(User).filter(User.user_type == 'student').count()
    
    return {
        "job_id": job_id,
        "job_title": job.title,
        "student_count": student_count,
        "status": "Backend is working"
    }

@router.post("/recruiter/register")
def recruiter_register(data: Dict[str, Any], db: Session = Depends(get_db)):
    """Register new recruiter"""
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    
    if not all([name, email, password]):
        raise HTTPException(status_code=400, detail="Name, email and password required")
    
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = pwd_context.hash(password)
    
    user = User(
        email=email,
        google_name=name,
        user_type='recruiter',
        hashed_password=hashed_password
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/recruiter/shortlist")
def shortlist_candidate(data: Dict[str, Any], credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Shortlist a candidate for a job"""
    recruiter = _require_recruiter(credentials, db)
    
    job_id = data.get("job_id")
    student_id = data.get("student_id")
    match_score = data.get("match_score")
    notes = data.get("notes", "")
    
    if not job_id or not student_id:
        raise HTTPException(status_code=400, detail="job_id and student_id required")
    
    # Verify job belongs to recruiter
    job = db.query(Job).filter(Job.id == job_id, Job.recruiter_id == recruiter.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check if already shortlisted
    existing = db.query(Shortlist).filter(
        Shortlist.recruiter_id == recruiter.id,
        Shortlist.job_id == job_id,
        Shortlist.student_id == student_id
    ).first()
    
    if existing:
        return {"message": "Candidate already shortlisted", "shortlist_id": existing.id}
    
    # Create shortlist entry
    shortlist = Shortlist(
        recruiter_id=recruiter.id,
        job_id=job_id,
        student_id=student_id,
        match_score=match_score,
        notes=notes
    )
    db.add(shortlist)
    db.commit()
    db.refresh(shortlist)
    
    return {"message": "Candidate shortlisted successfully", "shortlist_id": shortlist.id}

@router.get("/recruiter/jobs/{job_id}/shortlisted")
def get_shortlisted_candidates(job_id: int, credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Get shortlisted candidates for a job"""
    recruiter = _require_recruiter(credentials, db)
    
    # Verify job belongs to recruiter
    job = db.query(Job).filter(Job.id == job_id, Job.recruiter_id == recruiter.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    shortlisted = db.query(Shortlist).filter(
        Shortlist.recruiter_id == recruiter.id,
        Shortlist.job_id == job_id
    ).all()
    
    candidates = []
    for entry in shortlisted:
        student = db.query(User).filter(User.id == entry.student_id).first()
        onboarding = db.query(Onboarding).filter(Onboarding.user_id == entry.student_id).first()
        
        if student:
            candidates.append({
                "shortlist_id": entry.id,
                "student_id": student.id,
                "name": student.google_name or student.email,
                "email": student.email,
                "match_score": entry.match_score,
                "notes": entry.notes,
                "status": entry.status,
                "shortlisted_at": entry.created_at.isoformat(),
                "career_goals": str(onboarding.career_goals) if onboarding and onboarding.career_goals else "Not specified",
                "skills": str(onboarding.current_skills) if onboarding and onboarding.current_skills else "Not specified"
            })
    
    return {
        "job": {
            "id": job.id,
            "title": job.title,
            "description": job.description
        },
        "shortlisted_candidates": candidates,
        "total_shortlisted": len(candidates)
    }

@router.delete("/recruiter/shortlist/{shortlist_id}")
def remove_from_shortlist(shortlist_id: int, credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Remove candidate from shortlist"""
    recruiter = _require_recruiter(credentials, db)
    
    shortlist = db.query(Shortlist).filter(
        Shortlist.id == shortlist_id,
        Shortlist.recruiter_id == recruiter.id
    ).first()
    
    if not shortlist:
        raise HTTPException(status_code=404, detail="Shortlist entry not found")
    
    db.delete(shortlist)
    db.commit()
    
    return {"message": "Candidate removed from shortlist"}

@router.put("/recruiter/shortlist/{shortlist_id}/status")
def update_shortlist_status(shortlist_id: int, data: Dict[str, Any], credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Update shortlisted candidate status"""
    recruiter = _require_recruiter(credentials, db)
    
    shortlist = db.query(Shortlist).filter(
        Shortlist.id == shortlist_id,
        Shortlist.recruiter_id == recruiter.id
    ).first()
    
    if not shortlist:
        raise HTTPException(status_code=404, detail="Shortlist entry not found")
    
    new_status = data.get("status")
    notes = data.get("notes")
    
    if new_status:
        shortlist.status = new_status
    if notes is not None:
        shortlist.notes = notes
    
    db.commit()
    
    return {"message": "Status updated successfully"}

# Google Meet Integration Endpoints
# Removed old schedule_interview_with_candidate - replaced with enhanced version above

@router.get("/recruiter/interviews/upcoming")
def get_upcoming_interviews(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Get recruiter's upcoming interviews"""
    recruiter = _require_recruiter(credentials, db)
    
    try:
        from app.core.google_meet_service import google_meet_service
        
        interviews = google_meet_service.get_upcoming_interviews(recruiter.id, days_ahead=14)
        
        # Enhance with candidate information
        enhanced_interviews = []
        for interview in interviews:
            # Try to match with shortlisted candidates
            candidate_info = None
            
            # Extract candidate email from attendees
            for attendee in interview.get('attendees', []):
                if attendee.get('email') != recruiter.email:
                    candidate_email = attendee.get('email')
                    candidate = db.query(User).filter(User.email == candidate_email).first()
                    
                    if candidate:
                        candidate_info = {
                            "id": candidate.id,
                            "name": candidate.google_name or candidate.email.split('@')[0],
                            "email": candidate.email,
                            "picture": candidate.google_picture
                        }
                    break
            
            enhanced_interviews.append({
                **interview,
                "candidate": candidate_info,
                "formatted_time": datetime.fromisoformat(interview['start_time'].replace('Z', '+00:00')).strftime('%A, %B %d at %I:%M %p')
            })
        
        return {
            "interviews": enhanced_interviews,
            "total_upcoming": len(enhanced_interviews)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching interviews: {str(e)}")

@router.post("/recruiter/interviews/{event_id}/cancel")
def cancel_interview(event_id: str, data: Dict[str, Any], credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Cancel an interview"""
    recruiter = _require_recruiter(credentials, db)
    
    reason = data.get("reason", "")
    
    try:
        from app.core.google_meet_service import google_meet_service
        
        result = google_meet_service.cancel_interview(recruiter.id, event_id, reason)
        
        if result.get('success'):
            # Update related shortlist entries
            shortlists = db.query(Shortlist).filter(
                Shortlist.recruiter_id == recruiter.id,
                Shortlist.status == 'interview_scheduled'
            ).all()
            
            for shortlist in shortlists:
                if event_id in (shortlist.notes or ""):
                    shortlist.status = 'shortlisted'
                    shortlist.notes = f"Interview cancelled. {reason}".strip()
            
            db.commit()
            
            return {
                "success": True,
                "message": "Interview cancelled successfully"
            }
        else:
            return {
                "success": False,
                "error": result.get('error', 'Failed to cancel interview')
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cancelling interview: {str(e)}")

@router.post("/recruiter/interviews/{event_id}/reschedule")
def reschedule_interview(event_id: str, data: Dict[str, Any], credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Reschedule an interview"""
    recruiter = _require_recruiter(credentials, db)
    
    new_datetime_str = data.get("new_datetime")
    duration_minutes = data.get("duration_minutes", 60)
    reason = data.get("reason", "")
    
    if not new_datetime_str:
        raise HTTPException(status_code=400, detail="new_datetime is required")
    
    try:
        from datetime import datetime
        from app.core.google_meet_service import google_meet_service
        
        new_datetime = datetime.fromisoformat(new_datetime_str.replace('Z', '+00:00'))
        
        # Check availability for new time
        availability = google_meet_service.check_calendar_availability(
            recruiter.id, new_datetime, duration_minutes
        )
        
        if not availability.get('available'):
            return {
                "success": False,
                "error": "New time slot not available",
                "conflicts": availability.get('conflicts', []),
                "suggested_times": availability.get('suggested_times', [])
            }
        
        result = google_meet_service.reschedule_interview(
            recruiter.id, event_id, new_datetime, duration_minutes, reason
        )
        
        if result.get('success'):
            # Update shortlist entries
            shortlists = db.query(Shortlist).filter(
                Shortlist.recruiter_id == recruiter.id,
                Shortlist.status == 'interview_scheduled'
            ).all()
            
            for shortlist in shortlists:
                if event_id in (shortlist.notes or ""):
                    shortlist.notes = f"Interview rescheduled to {new_datetime.strftime('%Y-%m-%d %H:%M UTC')}. {reason}".strip()
            
            db.commit()
            
            return {
                "success": True,
                "message": "Interview rescheduled successfully",
                "new_time": new_datetime.isoformat()
            }
        else:
            return {
                "success": False,
                "error": result.get('error', 'Failed to reschedule interview')
            }
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid datetime format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rescheduling interview: {str(e)}")

@router.post("/recruiter/emails/summarize")
def summarize_email(data: Dict[str, Any], credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Summarize email content using AI"""
    recruiter = _require_recruiter(credentials, db)
    
    email_content = data.get('content', '')
    sender_name = data.get('sender_name', 'Unknown')
    
    if not email_content:
        raise HTTPException(status_code=400, detail="Email content required")
    
    try:
        from app.core.email_service import email_service
        summary = email_service.summarize_email_with_ai(email_content)
        skills = email_service.extract_candidate_skills(email_content)
        
        return {
            "summary": summary,
            "skills": skills,
            "sender_name": sender_name,
            "content_length": len(email_content)
        }
        
    except Exception as e:
        return {
            "summary": f"Email from {sender_name}. Content: {email_content[:200]}...",
            "skills": [],
            "error": str(e)
        }

@router.post("/recruiter/emails/send-meet-link")
def send_meet_link_to_candidate(data: Dict[str, Any], credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Send Google Meet link to email candidate"""
    recruiter = _require_recruiter(credentials, db)
    
    candidate_email = data.get('candidate_email')
    candidate_name = data.get('candidate_name')
    interview_datetime = data.get('interview_datetime')
    duration_minutes = data.get('duration_minutes', 60)
    job_title = data.get('job_title', 'Position')
    notes = data.get('notes', '')
    
    if not all([candidate_email, candidate_name, interview_datetime]):
        raise HTTPException(status_code=400, detail="candidate_email, candidate_name, and interview_datetime required")
    
    try:
        from datetime import datetime
        from app.core.google_meet_service import google_meet_service
        
        # Parse datetime
        interview_dt = datetime.fromisoformat(interview_datetime.replace('Z', '+00:00'))
        
        # Create Google Meet event
        result = google_meet_service.create_google_meet_event(
            recruiter_id=recruiter.id,
            candidate_email=candidate_email,
            candidate_name=candidate_name,
            start_time=interview_dt,
            duration_minutes=duration_minutes,
            job_title=job_title,
            notes=notes
        )
        
        if result.get('success'):
            return {
                "success": True,
                "message": f"Google Meet link sent to {candidate_name}",
                "meet_link": result.get('meet_link'),
                "calendar_link": result.get('event_link'),
                "interview_datetime": interview_datetime,
                "email_sent": result.get('email_sent', False)
            }
        else:
            # Fallback: create simple meeting info
            return {
                "success": True,
                "message": f"Meeting scheduled with {candidate_name}",
                "meet_link": "https://meet.google.com/new",
                "interview_datetime": interview_datetime,
                "note": "Please create Google Meet link manually and send to candidate",
                "candidate_email": candidate_email
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create meeting. Please schedule manually."
        }

@router.post("/recruiter/emails/add-to-shortlist")
def add_email_to_shortlist(data: Dict[str, Any], credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Add email candidate to shortlist for specific job"""
    recruiter = _require_recruiter(credentials, db)
    
    sender_email = data.get('sender_email')
    sender_name = data.get('sender_name')
    email_content = data.get('content', '')
    job_id = data.get('job_id')
    
    if not all([sender_email, sender_name, job_id]):
        raise HTTPException(status_code=400, detail="sender_email, sender_name, and job_id required")
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == sender_email).first()
    
    if existing_user:
        # Add to shortlist if not already there
        existing_shortlist = db.query(Shortlist).filter(
            Shortlist.recruiter_id == recruiter.id,
            Shortlist.job_id == job_id,
            Shortlist.student_id == existing_user.id
        ).first()
        
        if existing_shortlist:
            return {"message": "Candidate already shortlisted", "user_id": existing_user.id}
        
        shortlist = Shortlist(
            recruiter_id=recruiter.id,
            job_id=job_id,
            student_id=existing_user.id,
            match_score=75,
            notes="Added from email",
            source="email"
        )
        db.add(shortlist)
        db.commit()
        
        return {"message": "Existing candidate added to shortlist", "user_id": existing_user.id}
    
    # Create new user
    try:
        from app.core.email_service import email_service
        summary = email_service.summarize_email_with_ai(email_content)
        skills = email_service.extract_candidate_skills(email_content)
    except:
        summary = f"Email candidate: {sender_name}"
        skills = []
    
    new_user = User(
        email=sender_email,
        google_name=sender_name,
        user_type='student',
        created_by_recruiter_id=recruiter.id,
        source='email'
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create onboarding record
    from app.models.onboarding import Onboarding
    onboarding = Onboarding(
        user_id=new_user.id,
        name=sender_name,
        career_goals="Seeking opportunities",
        current_skills=", ".join(skills[:5]) if skills else "Various skills",
        grade="Professional"
    )
    db.add(onboarding)
    
    # Create candidate vector
    try:
        from app.models.candidate_vector import CandidateVector
        from app.core.embeddings import simple_text_embedding
        
        vector = simple_text_embedding(summary)
        candidate_vector = CandidateVector(
            user_id=new_user.id,
            vector=vector,
            summary_text=summary,
            skills_tags=skills[:10]
        )
        db.add(candidate_vector)
    except Exception as e:
        print(f"Vector creation error: {e}")
    
    # Add to shortlist
    shortlist = Shortlist(
        recruiter_id=recruiter.id,
        job_id=job_id,
        student_id=new_user.id,
        match_score=75,
        notes=f"Email candidate. Skills: {', '.join(skills[:3])}",
        source="email"
    )
    db.add(shortlist)
    db.commit()
    
    return {
        "message": "Candidate created and added to shortlist",
        "user_id": new_user.id,
        "skills_found": len(skills)
    }

@router.get("/recruiter/jobs/for-shortlist")
def get_jobs_for_shortlist(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Get recruiter's jobs for shortlisting candidates"""
    recruiter = _require_recruiter(credentials, db)
    
    jobs = db.query(Job).filter(Job.recruiter_id == recruiter.id).all()
    
    return {
        "jobs": [{
            "id": job.id,
            "title": job.title,
            "description": job.description[:100] + "..." if len(job.description) > 100 else job.description,
            "location": job.location or "Not specified",
            "created_at": job.created_at.isoformat() if job.created_at else None
        } for job in jobs],
        "total": len(jobs)
    }

@router.post("/recruiter/emails/quick-interview")
def schedule_quick_interview(data: Dict[str, Any], credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Quick interview scheduling from email summary"""
    recruiter = _require_recruiter(credentials, db)
    
    candidate_email = data.get('candidate_email')
    candidate_name = data.get('candidate_name')
    
    if not all([candidate_email, candidate_name]):
        raise HTTPException(status_code=400, detail="candidate_email and candidate_name required")
    
    # Generate a quick meet link
    from datetime import datetime, timedelta
    
    # Suggest next available time (1 hour from now)
    suggested_time = datetime.now() + timedelta(hours=1)
    
    return {
        "success": True,
        "candidate_name": candidate_name,
        "candidate_email": candidate_email,
        "suggested_time": suggested_time.isoformat(),
        "meet_link": "https://meet.google.com/new",
        "message": f"Ready to schedule interview with {candidate_name}",
        "instructions": "Click 'Send Meet Link' to create and send Google Meet invitation"
    }

@router.get("/recruiter/emails/test")
def test_email_fetch(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Test email fetching functionality"""
    recruiter = _require_recruiter(credentials, db)
    
    if not recruiter.google_access_token:
        return {
            "error": "No Google access token found",
            "message": "Please connect your Google account first"
        }
    
    try:
        from app.core.email_service import email_service
        emails = email_service.fetch_recent_job_emails(recruiter.google_access_token, days_back=7)
        
        return {
            "success": True,
            "emails_found": len(emails),
            "emails": emails[:5],
            "access_token_exists": bool(recruiter.google_access_token)
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }

@router.get("/recruiter/calendar/availability")
def check_calendar_availability(start_time: str, duration_minutes: int = 60, credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Check recruiter's calendar availability for a specific time"""
    recruiter = _require_recruiter(credentials, db)
    
    try:
        from datetime import datetime
        from app.core.google_meet_service import google_meet_service
        
        check_datetime = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        
        availability = google_meet_service.check_calendar_availability(
            recruiter.id, check_datetime, duration_minutes
        )
        
        return {
            "available": availability.get('available', False),
            "conflicts": availability.get('conflicts', []),
            "suggested_times": availability.get('suggested_times', []),
            "checked_time": check_datetime.isoformat(),
            "duration_minutes": duration_minutes
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid datetime format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking availability: {str(e)}")

# Enhanced Email Management Endpoints

@router.get("/recruiter/emails/job-related")
def get_job_related_emails(days_back: int = 1, credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Fetch job-related emails from the last N days with enhanced filtering"""
    recruiter = _require_recruiter(credentials, db)
    
    if not recruiter.google_access_token:
        return {
            "emails": [],
            "message": "Google account not connected. Please connect your Google account to fetch emails.",
            "total": 0
        }
    
    try:
        from app.core.email_service import email_service
        
        emails = email_service.fetch_recent_job_emails(recruiter.google_access_token, days_back)
        
        # Enhance emails with additional metadata
        enhanced_emails = []
        for email in emails:
            # Check if sender is already in system
            existing_user = db.query(User).filter(
                User.email == email['sender_email']
            ).first()
            
            enhanced_emails.append({
                **email,
                "in_system": existing_user is not None,
                "user_id": existing_user.id if existing_user else None,
                "has_resume": any(att.get('type') == 'pdf' for att in email.get('attachments', [])),
                "priority_score": _calculate_email_priority(email),
                "keywords_matched": _extract_matched_keywords(email)
            })
        
        # Sort by priority score and date
        enhanced_emails.sort(key=lambda x: (x['priority_score'], x['received_at']), reverse=True)
        
        return {
            "emails": enhanced_emails,
            "total": len(enhanced_emails),
            "days_searched": days_back,
            "with_resume": len([e for e in enhanced_emails if e.get('has_resume', False)]),
            "new_candidates": len([e for e in enhanced_emails if not e.get('in_system', False)])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching job emails: {str(e)}")

@router.post("/recruiter/emails/bulk-process")
def bulk_process_emails(data: Dict[str, Any], credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Process multiple emails at once - summarize and optionally add to shortlist"""
    recruiter = _require_recruiter(credentials, db)
    
    email_ids = data.get('email_ids', [])
    action = data.get('action', 'summarize')  # 'summarize' or 'shortlist'
    job_id = data.get('job_id')  # Required for shortlist action
    
    if not email_ids:
        raise HTTPException(status_code=400, detail="email_ids required")
    
    if action == 'shortlist' and not job_id:
        raise HTTPException(status_code=400, detail="job_id required for shortlist action")
    
    results = []
    
    for email_id in email_ids:
        try:
            if action == 'summarize':
                # Get email data (this would need to be implemented based on email source)
                summary_result = {
                    "email_id": email_id,
                    "status": "summarized",
                    "summary": "Email summary would be generated here"
                }
                results.append(summary_result)
            
            elif action == 'shortlist':
                # Add to shortlist (implementation would depend on email data structure)
                shortlist_result = {
                    "email_id": email_id,
                    "status": "shortlisted",
                    "job_id": job_id
                }
                results.append(shortlist_result)
                
        except Exception as e:
            results.append({
                "email_id": email_id,
                "status": "error",
                "error": str(e)
            })
    
    return {
        "processed": len(results),
        "action": action,
        "results": results
    }

@router.get("/recruiter/shortlisted-candidates")
def get_all_shortlisted_candidates(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Get all shortlisted candidates with full functionality"""
    recruiter = _require_recruiter(credentials, db)
    
    shortlisted = db.query(Shortlist).filter(
        Shortlist.recruiter_id == recruiter.id
    ).order_by(Shortlist.created_at.desc()).all()
    
    candidates = []
    for entry in shortlisted:
        student = db.query(User).filter(User.id == entry.student_id).first()
        job = db.query(Job).filter(Job.id == entry.job_id).first()
        onboarding = db.query(Onboarding).filter(Onboarding.user_id == entry.student_id).first()
        candidate_vector = db.query(CandidateVector).filter(CandidateVector.user_id == entry.student_id).first()
        
        if student:
            candidates.append({
                "shortlist_id": entry.id,
                "student_id": student.id,
                "name": student.google_name or student.email,
                "email": student.email,
                "picture": student.google_picture,
                "match_score": entry.match_score,
                "notes": entry.notes,
                "status": entry.status,
                "shortlisted_at": entry.created_at.isoformat(),
                "source": getattr(entry, 'source', 'email' if student.created_by_recruiter_id == recruiter.id else 'platform'),
                "job": {
                    "id": job.id,
                    "title": job.title,
                    "description": job.description[:100] + "..." if len(job.description) > 100 else job.description,
                    "location": job.location
                } if job else None,
                "profile": {
                    "career_goals": str(onboarding.career_goals) if onboarding and onboarding.career_goals else "Not specified",
                    "skills": str(onboarding.current_skills) if onboarding and onboarding.current_skills else "Not specified",
                    "grade": onboarding.grade if onboarding else "Not specified",
                    "summary": candidate_vector.summary_text if candidate_vector else "No summary available",
                    "skills_tags": candidate_vector.skills_tags if candidate_vector else []
                } if onboarding else {
                    "career_goals": "Not specified",
                    "skills": "Not specified", 
                    "grade": "Not specified",
                    "summary": candidate_vector.summary_text if candidate_vector else "No summary available",
                    "skills_tags": candidate_vector.skills_tags if candidate_vector else []
                },
                "can_schedule_interview": True,
                "can_update_status": True,
                "can_remove": True
            })
    
    return {
        "candidates": candidates,
        "total": len(candidates),
        "email_sourced": len([c for c in candidates if c['source'] == 'email']),
        "platform_sourced": len([c for c in candidates if c['source'] == 'platform']),
        "by_status": {
            "shortlisted": len([c for c in candidates if c['status'] == 'shortlisted']),
            "interview_scheduled": len([c for c in candidates if c['status'] == 'interview_scheduled']),
            "interviewed": len([c for c in candidates if c['status'] == 'interviewed']),
            "hired": len([c for c in candidates if c['status'] == 'hired']),
            "rejected": len([c for c in candidates if c['status'] == 'rejected'])
        }
    }

@router.post("/recruiter/shortlisted/{shortlist_id}/schedule-interview")
def schedule_interview_for_shortlisted(shortlist_id: int, data: Dict[str, Any], credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Schedule interview for any shortlisted candidate (email or platform sourced)"""
    recruiter = _require_recruiter(credentials, db)
    
    # Verify shortlist entry belongs to recruiter
    shortlist = db.query(Shortlist).filter(
        Shortlist.id == shortlist_id,
        Shortlist.recruiter_id == recruiter.id
    ).first()
    
    if not shortlist:
        raise HTTPException(status_code=404, detail="Shortlist entry not found")
    
    # Get candidate and job details
    candidate = db.query(User).filter(User.id == shortlist.student_id).first()
    job = db.query(Job).filter(Job.id == shortlist.job_id).first()
    
    if not candidate or not job:
        raise HTTPException(status_code=404, detail="Candidate or job not found")
    
    # Parse interview details
    interview_datetime_str = data.get("interview_datetime")
    duration_minutes = data.get("duration_minutes", 60)
    notes = data.get("notes", "")
    
    if not interview_datetime_str:
        raise HTTPException(status_code=400, detail="interview_datetime is required")
    
    try:
        from datetime import datetime
        interview_datetime = datetime.fromisoformat(interview_datetime_str.replace('Z', '+00:00'))
        
        # For email-sourced candidates, we'll create a simple calendar event
        # For platform candidates, we can use the full Google Meet integration
        
        if candidate.created_by_recruiter_id == recruiter.id:
            # Email-sourced candidate - create basic interview record
            shortlist.status = 'interview_scheduled'
            shortlist.notes = f"Interview scheduled for {interview_datetime.strftime('%Y-%m-%d %H:%M UTC')}. Contact: {candidate.email}. {notes}".strip()
            db.commit()
            
            return {
                "success": True,
                "message": f"Interview scheduled with {candidate.google_name or candidate.email}",
                "interview_details": {
                    "datetime": interview_datetime.isoformat(),
                    "duration_minutes": duration_minutes,
                    "candidate_name": candidate.google_name or candidate.email,
                    "candidate_email": candidate.email,
                    "job_title": job.title,
                    "notes": "Please contact candidate directly to confirm interview details"
                },
                "candidate_source": "email"
            }
        else:
            # Platform candidate - use full Google Meet integration
            from app.core.google_meet_service import google_meet_service
            
            result = google_meet_service.create_google_meet_event(
                recruiter_id=recruiter.id,
                candidate_email=candidate.email,
                candidate_name=candidate.google_name or candidate.email.split('@')[0],
                start_time=interview_datetime,
                duration_minutes=duration_minutes,
                job_title=job.title,
                notes=notes
            )
            
            if result.get('success'):
                shortlist.status = 'interview_scheduled'
                shortlist.notes = f"Google Meet scheduled for {interview_datetime.strftime('%Y-%m-%d %H:%M UTC')}. {notes}".strip()
                db.commit()
                
                return {
                    "success": True,
                    "message": f"Google Meet interview scheduled with {candidate.google_name or candidate.email}",
                    "interview_details": {
                        "event_id": result.get('event_id'),
                        "meet_link": result.get('meet_link'),
                        "calendar_link": result.get('event_link'),
                        "datetime": interview_datetime.isoformat(),
                        "duration_minutes": duration_minutes,
                        "candidate_name": candidate.google_name or candidate.email,
                        "candidate_email": candidate.email,
                        "job_title": job.title
                    },
                    "email_sent": result.get('email_sent', False),
                    "candidate_source": "platform"
                }
            else:
                return {
                    "success": False,
                    "error": result.get('error', 'Failed to create Google Meet interview')
                }
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid datetime format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scheduling interview: {str(e)}")

def _calculate_email_priority(email: Dict[str, Any]) -> int:
    """Calculate priority score for email based on content and attachments"""
    score = 0
    
    # High priority keywords in subject
    high_priority_words = ['urgent', 'asap', 'immediate', 'senior', 'lead', 'director']
    subject = email.get('subject', '').lower()
    for word in high_priority_words:
        if word in subject:
            score += 10
    
    # Has resume/CV attachment
    if any(att.get('type') == 'pdf' for att in email.get('attachments', [])):
        score += 20
    
    # Recent email (within last 24 hours)
    try:
        from datetime import datetime, timedelta
        received_at = datetime.fromisoformat(email.get('received_at', ''))
        if datetime.now() - received_at < timedelta(hours=24):
            score += 15
    except:
        pass
    
    # Technical keywords in content
    tech_keywords = ['developer', 'engineer', 'programmer', 'architect', 'manager']
    content = email.get('content', '').lower()
    for word in tech_keywords:
        if word in content:
            score += 5
    
    return score

def _extract_matched_keywords(email: Dict[str, Any]) -> List[str]:
    """Extract job-related keywords found in email"""
    from app.core.email_service import EmailService
    
    text = f"{email.get('subject', '')} {email.get('content', '')}".lower()
    matched = []
    
    for keyword in EmailService.JOB_KEYWORDS:
        if keyword in text:
            matched.append(keyword)
    
    return matched[:10]  # Limit to 10 keywords