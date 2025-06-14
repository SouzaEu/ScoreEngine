from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.sql import func

from app.db.base_class import Base

class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    score = Column(Float)
    features = Column(JSON)
    explanation = Column(JSON)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Score(user_id={self.user_id}, score={self.score}, timestamp={self.timestamp})>" 