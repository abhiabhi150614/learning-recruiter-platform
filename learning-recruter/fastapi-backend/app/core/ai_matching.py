from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from app.models.job import Job
from app.models.student_profile_summary import StudentProfileSummary
from app.models.user import User
from app.core.gemini_ai import chatbot
import json

def calculate_ai_match_percentage(job: Job, candidate_profile: StudentProfileSummary, user: User) -> Dict[str, Any]:
    """Use AI to calculate sophisticated match percentage between job and candidate"""
    
    try:
        # Prepare job requirements
        job_data = {
            "title": job.title,
            "description": job.description,
            "required_skills": job.required_skills or [],
            "experience_level": job.experience_level,
            "location": job.location,
            "salary_range": job.salary_range,
            "job_type": job.job_type
        }
        
        # Prepare candidate data
        candidate_data = {
            "name": user.google_name or user.email,
            "skills": candidate_profile.skills_tags or [],
            "summary": candidate_profile.summary_text,
            "interests": candidate_profile.interests or [],
            "profile_data": getattr(candidate_profile, 'profile_data', {})
        }
        
        # AI matching prompt
        prompt = f"""
Analyze the job-candidate match and provide a detailed assessment:

JOB REQUIREMENTS:
Title: {job_data['title']}
Description: {job_data['description']}
Required Skills: {', '.join(job_data['required_skills'])}
Experience Level: {job_data['experience_level']}
Location: {job_data['location']}
Type: {job_data['job_type']}

CANDIDATE PROFILE:
Name: {candidate_data['name']}
Skills: {', '.join(candidate_data['skills'])}
Summary: {candidate_data['summary']}
Interests: {', '.join(candidate_data['interests'])}

Provide analysis in this EXACT JSON format:
{{
    "match_percentage": [0-100 integer],
    "skill_match": [0-100 integer],
    "experience_match": [0-100 integer],
    "interest_alignment": [0-100 integer],
    "overall_fit": "[Excellent/Good/Fair/Poor]",
    "strengths": ["strength1", "strength2", "strength3"],
    "gaps": ["gap1", "gap2"],
    "recommendation": "[Strong Hire/Consider/Interview/Pass]",
    "reasoning": "Brief explanation of the match score"
}}

Be precise and realistic in scoring. Consider skill overlap, experience level alignment, and career interest match.
"""
        
        response = chatbot.model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Parse JSON response
        try:
            # Clean the response to extract JSON
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0]
            
            ai_analysis = json.loads(result_text)
            
            # Validate and ensure all required fields
            required_fields = ["match_percentage", "skill_match", "experience_match", "interest_alignment"]
            for field in required_fields:
                if field not in ai_analysis:
                    ai_analysis[field] = 50  # Default fallback
            
            # Ensure percentages are within valid range
            for field in required_fields:
                ai_analysis[field] = max(0, min(100, int(ai_analysis[field])))
            
            return ai_analysis
            
        except json.JSONDecodeError:
            # Fallback to basic matching if AI parsing fails
            return _fallback_matching(job_data, candidate_data)
            
    except Exception as e:
        print(f"AI matching error: {e}")
        return _fallback_matching(job_data, candidate_data)

def _fallback_matching(job_data: Dict, candidate_data: Dict) -> Dict[str, Any]:
    """Fallback matching algorithm if AI fails"""
    
    job_skills = set(skill.lower() for skill in job_data.get('required_skills', []))
    candidate_skills = set(skill.lower() for skill in candidate_data.get('skills', []))
    
    # Calculate skill overlap
    skill_overlap = len(job_skills.intersection(candidate_skills))
    total_job_skills = len(job_skills)
    
    skill_match = (skill_overlap / total_job_skills * 100) if total_job_skills > 0 else 0
    
    # Basic experience matching
    experience_match = 70  # Default moderate match
    
    # Interest alignment based on keywords
    interest_keywords = ' '.join(candidate_data.get('interests', [])).lower()
    job_keywords = f"{job_data.get('title', '')} {job_data.get('description', '')}".lower()
    
    interest_alignment = 60  # Default
    if any(keyword in job_keywords for keyword in interest_keywords.split()):
        interest_alignment = 80
    
    # Overall match
    match_percentage = int((skill_match * 0.5 + experience_match * 0.3 + interest_alignment * 0.2))
    
    return {
        "match_percentage": match_percentage,
        "skill_match": int(skill_match),
        "experience_match": experience_match,
        "interest_alignment": interest_alignment,
        "overall_fit": "Good" if match_percentage >= 70 else "Fair" if match_percentage >= 50 else "Poor",
        "strengths": list(job_skills.intersection(candidate_skills))[:3],
        "gaps": list(job_skills - candidate_skills)[:2],
        "recommendation": "Consider" if match_percentage >= 60 else "Interview" if match_percentage >= 40 else "Pass",
        "reasoning": f"Skill match: {int(skill_match)}%, Experience alignment: {experience_match}%"
    }

def get_top_matches_for_job(db: Session, job_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """Get top AI-matched candidates for a specific job"""
    
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return []
    
    # Get all candidates with profiles
    candidates = db.query(StudentProfileSummary, User).join(
        User, StudentProfileSummary.user_id == User.id
    ).filter(User.user_type == 'student').all()
    
    matches = []
    for profile, user in candidates:
        ai_match = calculate_ai_match_percentage(job, profile, user)
        
        matches.append({
            "user_id": user.id,
            "name": user.google_name or user.email,
            "email": user.email,
            "skills": profile.skills_tags or [],
            "summary": profile.summary_text,
            "ai_match": ai_match,
            "match_percentage": ai_match["match_percentage"]
        })
    
    # Sort by match percentage
    matches.sort(key=lambda x: x["match_percentage"], reverse=True)
    
    return matches[:limit]

def get_job_recommendations_for_candidate(db: Session, user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
    """Get AI-recommended jobs for a specific candidate"""
    
    profile = db.query(StudentProfileSummary).filter(StudentProfileSummary.user_id == user_id).first()
    user = db.query(User).filter(User.id == user_id).first()
    
    if not profile or not user:
        return []
    
    # Get all active jobs
    jobs = db.query(Job).filter(Job.status == 'active').all()
    
    recommendations = []
    for job in jobs:
        ai_match = calculate_ai_match_percentage(job, profile, user)
        
        recommendations.append({
            "job_id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "salary_range": job.salary_range,
            "required_skills": job.required_skills or [],
            "ai_match": ai_match,
            "match_percentage": ai_match["match_percentage"]
        })
    
    # Sort by match percentage
    recommendations.sort(key=lambda x: x["match_percentage"], reverse=True)
    
    return recommendations[:limit]