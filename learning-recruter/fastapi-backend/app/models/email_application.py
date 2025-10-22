from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database.db import Base
from datetime import datetime

class EmailApplication(Base):
    __tablename__ = "email_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    recruiter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sender_email = Column(String(255), nullable=False)
    sender_name = Column(String(255))
    subject = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    attachments = Column(JSON, default=[])
    received_at = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    priority_score = Column(Integer, default=0)
    keywords_matched = Column(JSON, default=[])
    
    recruiter = relationship("User", foreign_keys=[recruiter_id])
    student = relationship("User", foreign_keys=[student_id])