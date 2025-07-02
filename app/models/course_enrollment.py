from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import uuid

Base = declarative_base()
class CompletionStatus(enum.Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

class CourseEnrollment(Base):
    __tablename__ = "Course_Enrollment"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), index=True)
    course_id = Column(String(36), ForeignKey("courses.id"), index=True)
    enrollment_date = Column(DateTime, default=func.now())
    completion_status = Column(Enum(CompletionStatus), default=CompletionStatus.IN_PROGRESS)
    progress_percentage = Column(Float, default=0)
    completion_date = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="courseEnrollments")
    course = relationship("Course", back_populates="enrollments")
