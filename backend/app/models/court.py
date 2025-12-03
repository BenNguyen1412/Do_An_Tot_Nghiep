from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Court(Base):
    """Main venue/court complex model"""
    __tablename__ = "courts"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    district = Column(String, nullable=False)
    city = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    court_quantity = Column(Integer, nullable=False, default=1)  # Number of individual courts
    opening_time = Column(String, nullable=False)  # Format: "HH:MM"
    closing_time = Column(String, nullable=False)  # Format: "HH:MM"
    facilities = Column(JSON, nullable=True)  # List of facility IDs
    contact_phone = Column(String, nullable=False)
    contact_email = Column(String, nullable=True)
    images = Column(JSON, nullable=True)  # List of image URLs
    time_slots = Column(JSON, nullable=True)  # Pricing by time slots
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="courts")
    individual_courts = relationship("IndividualCourt", back_populates="court", cascade="all, delete-orphan")


class IndividualCourt(Base):
    """Individual court within a venue"""
    __tablename__ = "individual_courts"

    id = Column(Integer, primary_key=True, index=True)
    court_id = Column(Integer, ForeignKey("courts.id"), nullable=False)
    name = Column(String, nullable=False)  # e.g., "Sân 1", "Sân VIP A"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    court = relationship("Court", back_populates="individual_courts")
    bookings = relationship("Booking", back_populates="individual_court", cascade="all, delete-orphan")


class Booking(Base):
    """Booking for an individual court"""
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    individual_court_id = Column(Integer, ForeignKey("individual_courts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    booking_date = Column(DateTime(timezone=True), nullable=False)
    start_time = Column(String, nullable=False)  # Format: "HH:MM"
    end_time = Column(String, nullable=False)  # Format: "HH:MM"
    phone_number = Column(String, nullable=False)
    status = Column(String, default="active")  # active, completed, cancelled
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    individual_court = relationship("IndividualCourt", back_populates="bookings")
    user = relationship("User", back_populates="bookings")
