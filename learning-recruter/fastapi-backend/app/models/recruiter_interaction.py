from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from app.database.db import Base


class RecruiterInteraction(Base):
    __tablename__ = "recruiter_interactions"

    id = Column(Integer, primary_key=True)
    recruiter_id = Column(Integer, ForeignKey("recruiters.id"), index=True)
    candidate_id = Column(Integer, ForeignKey("users.id"), index=True)
    interaction_type = Column(String)  # email_sent, profile_viewed, interview_scheduled, etc.
    details = Column(JSONB)  # store interaction metadata
    notes = Column(Text)
    status = Column(String, default="active")  # active, archived, rejected, hired
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class JobPosting(Base):
    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True)
    recruiter_id = Column(Integer, ForeignKey("recruiters.id"), index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    requirements = Column(JSONB)  # list of requirements
    skills = Column(JSONB)  # list of required skills
    location = Column(String)
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    is_active = Column(String, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class CandidateMatch(Base):
    __tablename__ = "candidate_matches"

    id = Column(Integer, primary_key=True)
    recruiter_id = Column(Integer, ForeignKey("recruiters.id"), index=True)
    job_id = Column(Integer, ForeignKey("job_postings.id"), index=True)
    candidate_id = Column(Integer, ForeignKey("users.id"), index=True)
    match_score = Column(String)  # store as string to avoid float precision issues
    match_reasons = Column(JSONB)  # list of match reasons
    status = Column(String, default="new")  # new, contacted, interview, offer, hired, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)