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
    images: Optional[List[str]] = None
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
        bookings = list(getattr(obj, 'bookings', []) or [])

        # Keep availability computed from effective active status (legacy + new enum field).
        has_active_bookings = any(
            (
                str(getattr(booking, 'status', '') or '').strip().lower() == 'active'
                or str(getattr(getattr(booking, 'booking_status', ''), 'value', getattr(booking, 'booking_status', '')) or '').strip().lower() == 'active'
            )
            for booking in bookings
        )
        
        data = {
            'id': obj.id,
            'court_id': obj.court_id,
            'name': obj.name,
            'is_active': obj.is_active,
            'is_available': not has_active_bookings and obj.is_active,
            'created_at': obj.created_at,
            'updated_at': obj.updated_at,
        }

        # IndividualCourtWithBookings extends this schema and needs nested bookings.
        if hasattr(cls, 'model_fields') and 'bookings' in getattr(cls, 'model_fields', {}):
            data['bookings'] = bookings

        return cls(**data)


# Booking Schemas
class BookingBase(BaseModel):
    booking_date: datetime
    start_time: str
    end_time: str
    phone_number: str
    customer_name: Optional[str] = None  # Name of customer (for owner bookings)
    customer_email: Optional[str] = None


class BookingCreate(BookingBase):
    individual_court_id: int
    payment_method: str = "vietqr"  # vietqr or cash


class BookingUpdate(BaseModel):
    status: Optional[str] = None
    booking_status: Optional[str] = None
    payment_status: Optional[str] = None


class Booking(BookingBase):
    id: int
    individual_court_id: int
    user_id: int
    status: Optional[str] = "active"  # Legacy status field (kept for backward compatibility)
    
    # Payment fields
    total_hours: Optional[float] = None
    total_price: Optional[float] = None
    payment_method: Optional[str] = None
    payment_status: Optional[str] = None
    booking_status: Optional[str] = None
    qr_code_url: Optional[str] = None
    bank_transaction_id: Optional[str] = None
    payment_verified_at: Optional[datetime] = None
    payment_note: Optional[str] = None
    
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Payment info response
class PaymentInfo(BaseModel):
    """Payment information for a booking"""
    qr_code_url: str
    bank_name: str
    account_number: str
    account_name: str
    amount: float
    content: str
    booking_id: Optional[int] = None
    expires_at: datetime


class PaymentPreviewRequest(BaseModel):
    """Request payload to preview VietQR payment before creating booking"""
    court_id: int
    booking_date: datetime
    start_time: str
    end_time: str


# Booking with payment info
class BookingWithPayment(Booking):
    payment_info: Optional[PaymentInfo] = None


# Response schemas with relationships
class IndividualCourtWithBookings(IndividualCourt):
    bookings: List[Booking] = []


# Owner info for court details
class CourtOwner(BaseModel):
    id: int
    full_name: str
    email: str
    phone_number: Optional[str] = None

    class Config:
        from_attributes = True


class CourtWithIndividualCourts(Court):
    individual_courts: List[IndividualCourt] = []
    owner: Optional[CourtOwner] = None


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


class UserBookingHistoryItem(BaseModel):
    id: int
    court_name: str
    location: str
    booking_date: datetime
    start_time: str
    end_time: str
    total_hours: Optional[float] = None
    total_price: Optional[float] = None
    status: str


class BookingInviteCodeCreateResponse(BaseModel):
    booking_id: int
    code: str
    status: str
    created_at: datetime


class BookingInviteCodePreviewRequest(BaseModel):
    code: str


class BookingInviteCodePreviewResponse(BaseModel):
    booking_id: int
    code: str
    court_name: str
    booking_date: datetime
    start_time: str
    end_time: str
    inviter_name: str
    status: str


class BookingInviteCodeActionRequest(BaseModel):
    code: str
    action: str  # accept or reject


class BookingInviteCodeActionResponse(BaseModel):
    booking_id: int
    code: str
    status: str
    message: str
    responded_at: Optional[datetime] = None


class BookingInviteSendRequest(BaseModel):
    code: str
    friend_user_id: int


class BookingInviteSendResponse(BaseModel):
    invite_id: int
    booking_id: int
    code: str
    invitee_user_id: int
    status: str
    message: str


class BookingInviteNotificationActionRequest(BaseModel):
    action: str  # accept or reject


class BookingInviteNotificationActionResponse(BaseModel):
    invite_id: int
    booking_id: int
    code: str
    status: str
    message: str
    responded_at: Optional[datetime] = None


class BookingInviteDetailResponse(BaseModel):
    invite_id: int
    booking_id: int
    code: str
    status: str
    court_name: str
    location: str
    booking_date: datetime
    start_time: str
    end_time: str
    total_price: Optional[float] = None
    inviter_name: str
    invitee_name: Optional[str] = None
