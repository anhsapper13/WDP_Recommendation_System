
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import uuid


Base = declarative_base()

class AppointmentType(enum.Enum):
    IN_PERSON = "IN_PERSON"
    VIDEO_CALL = "VIDEO_CALL"
    
class BookingStatus(enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"))
    consultant_id = Column(String(36), ForeignKey("users.id"))
    booking_time = Column(DateTime)
    end_time = Column(DateTime)
    appointment_type = Column(Enum(AppointmentType), default=AppointmentType.IN_PERSON)
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING)
    notes = Column(Text, nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(255), nullable=True)
    meeting_link = Column(String(255), nullable=True)
    reason = Column(String(255), nullable=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="appointments")
    consultant = relationship("User", foreign_keys=[consultant_id], back_populates="consultantAppointments")