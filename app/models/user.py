from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, Float, ForeignKey, Enum, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import uuid

Base = declarative_base()
# Enum for user roles
class UserRole(enum.Enum):
    ADMIN = "admin"
    CONSULTANT = "consultant"
    MEMBER = "member",
    GUEST = "guest"
    MANAGER = "manager"
    STAFF = "staff"


# Models
class User(Base):
    __tablename__ = "Users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(255))
    last_name = Column(String(255))
    role = Column(Enum(UserRole), default=UserRole.MEMBER)
    # Relationships
    consultantProfile = relationship("Consultant", back_populates="user", uselist=False)
    appointments = relationship("Appointment", foreign_keys="Appointment.user_id", back_populates="user")
    consultantAppointments = relationship("Appointment", foreign_keys="Appointment.consultant_id", back_populates="consultant")
    courseEnrollments = relationship("CourseEnrollment", back_populates="user")
    courseReviews = relationship("CourseReview", back_populates="user")
