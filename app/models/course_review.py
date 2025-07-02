from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, Float, ForeignKey, Enum, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class CourseReview(Base):
    __tablename__ = "Course_Review"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id = Column(String(36), ForeignKey("courses.id"), index=True)
    user_id = Column(String(36), ForeignKey("users.id"), index=True)
    rating = Column(Integer, default=1)
    review_text = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    course = relationship("Course", back_populates="reviews")
    user = relationship("User", back_populates="courseReviews")
    
