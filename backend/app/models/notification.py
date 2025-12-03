from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Notification(Base):
    """Notification model for users"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String, nullable=False)  # request_created, request_approved, request_rejected, booking_created, booking_cancelled
    related_id = Column(Integer, nullable=True)  # ID of related entity (court_request_id, booking_id, etc.)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="notifications")


class CourtRequest(Base):
    """Court registration request model"""
    __tablename__ = "court_requests"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Court information (same as Court model)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    district = Column(String, nullable=False)
    city = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    court_quantity = Column(Integer, nullable=False, default=1)
    opening_time = Column(String, nullable=False)
    closing_time = Column(String, nullable=False)
    facilities = Column(String, nullable=True)  # JSON string
    contact_phone = Column(String, nullable=False)
    contact_email = Column(String, nullable=True)
    images = Column(String, nullable=True)  # JSON string - list of image URLs
    time_slots = Column(String, nullable=True)  # JSON string
    
    status = Column(String, default="pending")  # pending, approved, rejected
    rejection_reason = Column(Text, nullable=True)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("User", foreign_keys=[owner_id], back_populates="court_requests")
    reviewer = relationship("User", foreign_keys=[reviewed_by])
