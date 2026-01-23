from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Time Slot Schema
class TimeSlot(BaseModel):
    start_time: str
    end_time: str
    price: float

    class Config:
        populate_by_name = True


# Court Schemas
class CourtBase(BaseModel):
    name: str
    address: str
    district: str
    city: str
    description: Optional[str] = None
    court_quantity: int = Field(ge=1)
    opening_time: str
    closing_time: str
    facilities: Optional[List[str]] = []
    contact_phone: str
    contact_email: Optional[str] = None
    time_slots: Optional[List[TimeSlot]] = []


class CourtCreate(CourtBase):
    pass


class CourtUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    district: Optional[str] = None
    city: Optional[str] = None
    description: Optional[str] = None
    court_quantity: Optional[int] = Field(None, ge=1)
    opening_time: Optional[str] = None
    closing_time: Optional[str] = None
    facilities: Optional[List[str]] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    time_slots: Optional[List[TimeSlot]] = None
    is_active: Optional[bool] = None


class Court(CourtBase):
    id: int
    owner_id: int
    images: Optional[List[str]] = []
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Individual Court Schemas
class IndividualCourtBase(BaseModel):
    name: str


class IndividualCourtCreate(IndividualCourtBase):
    court_id: int


class IndividualCourtUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None


class IndividualCourt(IndividualCourtBase):
    id: int
    court_id: int
    is_active: bool
    is_available: bool = True  # Computed: true if no active bookings
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm(cls, obj):
        # Check if court has any active bookings
        has_active_bookings = any(
            booking.status == 'active' 
            for booking in obj.bookings
        ) if hasattr(obj, 'bookings') else False
        
        data = {
            'id': obj.id,
            'court_id': obj.court_id,
            'name': obj.name,
            'is_active': obj.is_active,
            'is_available': not has_active_bookings and obj.is_active,
            'created_at': obj.created_at,
            'updated_at': obj.updated_at,
        }
        return cls(**data)


# Booking Schemas
class BookingBase(BaseModel):
    booking_date: datetime
    start_time: str
    end_time: str
    phone_number: str
    customer_name: Optional[str] = None  # Name of customer (for owner bookings)


class BookingCreate(BookingBase):
    individual_court_id: int


class BookingUpdate(BaseModel):
    status: Optional[str] = None


class Booking(BookingBase):
    id: int
    individual_court_id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Response schemas with relationships
class IndividualCourtWithBookings(IndividualCourt):
    bookings: List[Booking] = []


class CourtWithIndividualCourts(Court):
    individual_courts: List[IndividualCourt] = []


# User info for booking details
class BookingUser(BaseModel):
    id: int
    full_name: str
    email: str
    phone_number: Optional[str] = None

    class Config:
        from_attributes = True


# Detailed booking with court and user info
class BookingDetail(Booking):
    individual_court: IndividualCourt
    user: BookingUser
    court_name: Optional[str] = None  # Court complex name
    
    class Config:
        from_attributes = True


# Summary response for owner bookings
class OwnerBookingsSummary(BaseModel):
    total_bookings: int
    active_bookings: int
    completed_bookings: int
    cancelled_bookings: int
    period_days: int
