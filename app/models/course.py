from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import uuid


class CourseStatus(enum.Enum):
    WAITING_APPROVE = "WAITING_APPROVE"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class CourseContentType(enum.Enum):
    ALL = "ALL"
    BEGINNERS = "BEGINNERS"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"

Base = declarative_base()

class Course(Base):
    __tablename__ = "Course"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    status = Column(Enum(CourseStatus), default=CourseStatus.WAITING_APPROVE)
    avatar_url = Column(String(255), nullable=True)
    featured_image_url = Column(String(255), nullable=True)
    promo_video_url = Column(String(255), nullable=True)
    target_audience = Column(Enum(CourseContentType), default=CourseContentType.ALL)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    duration_minutes = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    category_id = Column(String(36), ForeignKey("course_categories.id"), index=True)
    
    # Relationships
    enrollments = relationship("CourseEnrollment", back_populates="course")
    reviews = relationship("CourseReview", back_populates="course")
    category = relationship("CourseCategory", back_populates="courses")
