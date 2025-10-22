from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text, String
from sqlalchemy.orm import relationship
from app.database.db import Base
from datetime import datetime

class Shortlist(Base):
    __tablename__ = "shortlists"
    
    id = Column(Integer, primary_key=True, index=True)
    recruiter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    match_score = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(String(50), default="shortlisted")  # shortlisted, interview_scheduled, interviewed, hired, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    source = Column(String(20), default="platform")  # platform, email
    
    # Relationships
    recruiter = relationship("User", foreign_keys=[recruiter_id])
    job = relationship("Job", foreign_keys=[job_id])
    student = relationship("User", foreign_keys=[student_id])