from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from app.database.db import Base


class StudentProfileSummary(Base):
    __tablename__ = "student_profile_summaries"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    summary_text = Column(String)
    interests = Column(JSONB)          # list[str]
    skills_tags = Column(JSONB)        # list[str]
    vector = Column(JSONB)             # list[float]
    graph_neighbors = Column(JSONB)    # [{user_id, weight}] precomputed related
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


