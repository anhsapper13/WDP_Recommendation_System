
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import uuid

Base = declarative_base()
class Consultant(Base):
    __tablename__ = "consultants"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), unique=True)
    qualifications = Column(JSON)  # Stores degrees, certifications as JSON array
    experience_years = Column(Integer)
    specialization = Column(String(255))
    bio = Column(Text, nullable=True)
    is_available = Column(Boolean, default=True)
    duration_time_slot = Column(Integer, default=30)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="consultantProfile")