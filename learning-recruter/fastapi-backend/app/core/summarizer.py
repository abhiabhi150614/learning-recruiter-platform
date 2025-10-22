from typing import Dict
from app.core.gemini_ai import chatbot


def summarize_learning(onboarding: Dict, months_completed: int, skills_observed: str = "") -> str:
    """Use Gemini to summarize a learner's progress into a concise recruiter-facing brief."""
    profile = f"""
Name: {onboarding.get('name')}
Grade: {onboarding.get('grade')}
Career Goals: {onboarding.get('career_goals')}
Current Skills: {onboarding.get('current_skills')}
Daily Time: {onboarding.get('time_commitment')}
Months Completed: {months_completed}
Skills Observed: {skills_observed}
"""
    prompt = f"""
Produce a concise recruiter-facing summary (max 150 words) of the learner's progress and capabilities.
Highlight concrete skills, demonstrated consistency, and areas of strength. Avoid fluff.

PROFILE:
{profile}
Return only plain text.
"""
    try:
        resp = chatbot.model.generate_content(prompt)
        return (resp.text or "").strip()
    except Exception:
        return "Learner shows consistent progress with practical skill development across completed months."


