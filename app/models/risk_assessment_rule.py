from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, Float, ForeignKey, Enum
from sqlalchemy.sql import func
import enum
import uuid
from app.database.database import Base

class RiskLevel(enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class RiskAssessmentRule(Base):
    __tablename__ = "risk_assessment_rules"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    survey_type_id = Column(String(36))  # Changed from survey_category_id
    min_score = Column(Integer, nullable=False)
    max_score = Column(Integer, nullable=False)
    risk_level = Column(Enum(RiskLevel), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())