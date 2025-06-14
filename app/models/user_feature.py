from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func

from app.db.base_class import Base

class UserFeature(Base):
    __tablename__ = "user_features"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)
    feature_data = Column(JSON)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<UserFeature(user_id={self.user_id}, last_updated={self.last_updated})>" 