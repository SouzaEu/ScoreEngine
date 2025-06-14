from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func

from app.db.base_class import Base

class ScoreContest(Base):
    __tablename__ = "score_contests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    reason = Column(Text)
    status = Column(String, default="pending")  # pending, approved, rejected
    resolution = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<ScoreContest(user_id={self.user_id}, status={self.status}, timestamp={self.timestamp})>" 