from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class TestSurvey(Base):
    __tablename__ = "Test_Survey"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    target_audience = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    estimated_time_minutes = Column(Integer, default=20)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    category_id = Column(String(36), ForeignKey("Survey_Category.id"), index=True)
    is_active = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    category = relationship("SurveyCategory", back_populates="test_surveys")
    questions = relationship("TestSurveyQuestion", back_populates="test_survey")
    attempts = relationship("SurveyAttempt", back_populates="test_survey")