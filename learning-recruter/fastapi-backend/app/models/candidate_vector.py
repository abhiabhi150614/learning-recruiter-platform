from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from app.database.db import Base


class CandidateVector(Base):
    __tablename__ = "candidate_vectors"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    vector = Column(JSONB)  # store as list[float] for portability
    summary_text = Column(String)
    skills_tags = Column(JSONB)  # list[str]
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


