from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, Float, ForeignKey, Enum, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import uuid

class RiskLevel(enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

Base = declarative_base()
class SurveyAttempt(Base):
    __tablename__ = "survey_attempts"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), index=True)
    test_survey_id = Column(String(36))
    completed_at = Column(DateTime, nullable=True)
    total_score = Column(Integer, default=0)
    risk_level = Column(Enum(), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    