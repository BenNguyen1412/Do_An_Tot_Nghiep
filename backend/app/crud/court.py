from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from datetime import datetime, timedelta
from app.models.court import Court, IndividualCourt, Booking
from app.schemas.court import CourtCreate, CourtUpdate, IndividualCourtCreate, IndividualCourtUpdate, BookingCreate, BookingUpdate

# Court CRUD
def get_court(db: Session, court_id: int) -> Optional[Court]:
    """Get a court by ID"""
    return db.query(Court).filter(Court.id == court_id).first()


def get_courts(db: Session, skip: int = 0, limit: int = 100) -> List[Court]:
    """Get all courts"""
    return db.query(Court).offset(skip).limit(limit).all()


def get_courts_by_owner(db: Session, owner_id: int) -> List[Court]:
    """Get all courts owned by a specific owner"""
    return db.query(Court).filter(Court.owner_id == owner_id).all()


def create_court(db: Session, court: CourtCreate, owner_id: int, images: Optional[List[str]] = None) -> Court:
    """Create a new court and auto-generate individual courts based on quantity"""
    # Convert time_slots to dict format for JSON storage
    time_slots_dict = [slot.model_dump() for slot in court.time_slots] if court.time_slots else []
    
    db_court = Court(
        owner_id=owner_id,
        name=court.name,
        address=court.address,
        district=court.district,
        city=court.city,
        description=court.description,
        court_quantity=court.court_quantity,
        opening_time=court.opening_time,
        closing_time=court.closing_time,
        facilities=court.facilities,
        contact_phone=court.contact_phone,
        contact_email=court.contact_email,
        images=images or [],
        time_slots=time_slots_dict,
    )
    db.add(db_court)
    db.commit()
    db.refresh(db_court)
    
    # Auto-generate individual courts based on quantity
    for i in range(1, court.court_quantity + 1):
        individual_court = IndividualCourt(
            court_id=db_court.id,
            name=f"Sân {i}"
        )
        db.add(individual_court)
    
    db.commit()
    db.refresh(db_court)
    
    return db_court


def update_court(db: Session, court_id: int, court_update: CourtUpdate) -> Optional[Court]:
    """Update a court"""
    db_court = get_court(db, court_id)
    if not db_court:
        return None
    
    update_data = court_update.model_dump(exclude_unset=True)
    
    # Convert time_slots if present (time_slots are already dicts from model_dump)
    if "time_slots" in update_data and update_data["time_slots"]:
        # time_slots are already in dict format, no need to convert
        pass
    
    for field, value in update_data.items():
        setattr(db_court, field, value)
    
    # If court_quantity changed, adjust individual courts
    if "court_quantity" in update_data:
        current_count = len(db_court.individual_courts)
        new_count = update_data["court_quantity"]
        
        if new_count > current_count:
            # Add more courts
            for i in range(current_count + 1, new_count + 1):
                individual_court = IndividualCourt(
                    court_id=court_id,
                    name=f"Sân {i}"
                )
                db.add(individual_court)
        elif new_count < current_count:
            # Remove excess courts (only if they have no bookings)
            courts_to_remove = db.query(IndividualCourt).filter(
                IndividualCourt.court_id == court_id
            ).order_by(IndividualCourt.id.desc()).limit(current_count - new_count).all()
            
            for court in courts_to_remove:
                if not court.bookings:
                    db.delete(court)
    
    db.commit()
    db.refresh(db_court)
    return db_court


def delete_court(db: Session, court_id: int) -> bool:
    """Delete a court"""
    db_court = get_court(db, court_id)
    if not db_court:
        return False
    
    db.delete(db_court)
    db.commit()
    return True


# Individual Court CRUD
def get_individual_court(db: Session, individual_court_id: int) -> Optional[IndividualCourt]:
    """Get an individual court by ID"""
    return db.query(IndividualCourt).filter(IndividualCourt.id == individual_court_id).first()


def get_individual_courts_by_court(db: Session, court_id: int) -> List[IndividualCourt]:
    """Get all individual courts for a specific court"""
    return db.query(IndividualCourt).filter(IndividualCourt.court_id == court_id).all()


def update_individual_court(db: Session, individual_court_id: int, individual_court_update: IndividualCourtUpdate) -> Optional[IndividualCourt]:
    """Update an individual court"""
    db_individual_court = get_individual_court(db, individual_court_id)
    if not db_individual_court:
        return None
    
    update_data = individual_court_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_individual_court, field, value)
    
    db.commit()
    db.refresh(db_individual_court)
    return db_individual_court


# Booking CRUD
def get_booking(db: Session, booking_id: int) -> Optional[Booking]:
    """Get a booking by ID"""
    return db.query(Booking).filter(Booking.id == booking_id).first()


def get_bookings_by_user(db: Session, user_id: int) -> List[Booking]:
    """Get all bookings for a user"""
    return db.query(Booking).filter(Booking.user_id == user_id).all()


def get_bookings_by_individual_court(db: Session, individual_court_id: int) -> List[Booking]:
    """Get all bookings for an individual court"""
    return db.query(Booking).filter(Booking.individual_court_id == individual_court_id).all()


def check_booking_overlap(db: Session, individual_court_id: int, booking_date, start_time: str, end_time: str, exclude_booking_id: int = None) -> bool:
    """Check if a booking overlaps with existing bookings"""
    from datetime import datetime
    
    # Get the date only (without time)
    booking_date_only = booking_date.date() if hasattr(booking_date, 'date') else booking_date
    
    # Query all active bookings for the same court and date
    query = db.query(Booking).filter(
        Booking.individual_court_id == individual_court_id,
        Booking.status == 'active'
    )
    
    # Exclude current booking if updating
    if exclude_booking_id:
        query = query.filter(Booking.id != exclude_booking_id)
    
    bookings = query.all()
    
    # Filter by date (comparing date only)
    bookings = [b for b in bookings if b.booking_date.date() == booking_date_only]
    
    # Check time overlap
    for existing_booking in bookings:
        # Time overlap if:
        # new_start < existing_end AND new_end > existing_start
        if start_time < existing_booking.end_time and end_time > existing_booking.start_time:
            return True
    
    return False


def find_available_courts(db: Session, court_id: int, booking_date, start_time: str, end_time: str, exclude_court_id: int = None) -> List[IndividualCourt]:
    """Find all individual courts in the same venue that are available for the given time slot"""
    from datetime import datetime
    
    # Get the date only (without time)
    booking_date_only = booking_date.date() if hasattr(booking_date, 'date') else booking_date
    
    # Get all individual courts for this venue
    all_courts = get_individual_courts_by_court(db, court_id)
    
    # Filter out the excluded court if provided
    if exclude_court_id:
        all_courts = [c for c in all_courts if c.id != exclude_court_id]
    
    available_courts = []
    
    for court in all_courts:
        # Check if this court has any overlapping bookings
        has_conflict = check_booking_overlap(db, court.id, booking_date, start_time, end_time)
        
        if not has_conflict:
            available_courts.append(court)
    
    return available_courts


def create_booking(db: Session, booking: BookingCreate, user_id: int) -> Booking:
    """Create a new booking"""
    # Check for booking overlap
    if check_booking_overlap(db, booking.individual_court_id, booking.booking_date, booking.start_time, booking.end_time):
        raise ValueError("Sân đã được đặt trong khung giờ này. Vui lòng chọn khung giờ khác.")
    
    db_booking = Booking(
        individual_court_id=booking.individual_court_id,
        user_id=user_id,
        booking_date=booking.booking_date,
        start_time=booking.start_time,
        end_time=booking.end_time,
        phone_number=booking.phone_number,
        customer_name=booking.customer_name,  # Store customer name if provided
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking


def update_booking(db: Session, booking_id: int, booking_update: BookingUpdate) -> Optional[Booking]:
    """Update a booking"""
    db_booking = get_booking(db, booking_id)
    if not db_booking:
        return None
    
    update_data = booking_update.model_dump(exclude_unset=True)
    
    # Check for booking overlap if time or date is being updated
    if any(key in update_data for key in ['booking_date', 'start_time', 'end_time']):
        # Use updated values or existing values
        check_date = update_data.get('booking_date', db_booking.booking_date)
        check_start = update_data.get('start_time', db_booking.start_time)
        check_end = update_data.get('end_time', db_booking.end_time)
        
        if check_booking_overlap(db, db_booking.individual_court_id, check_date, check_start, check_end, exclude_booking_id=booking_id):
            raise ValueError("Sân đã được đặt trong khung giờ này. Vui lòng chọn khung giờ khác.")
    
    for field, value in update_data.items():
        setattr(db_booking, field, value)
    
    db.commit()
    db.refresh(db_booking)
    return db_booking


def delete_booking(db: Session, booking_id: int) -> bool:
    """Delete a booking"""
    db_booking = get_booking(db, booking_id)
    if not db_booking:
        return False
    
    db.delete(db_booking)
    db.commit()
    return True


def get_bookings_by_owner(
    db: Session, 
    owner_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    court_id: Optional[int] = None,
    individual_court_id: Optional[int] = None,
    status: Optional[str] = None
) -> List[Booking]:
    """
    Get all bookings for courts owned by a specific owner with optional filters
    
    Args:
        owner_id: The owner's user ID
        start_date: Filter bookings from this date onwards
        end_date: Filter bookings up to this date
        court_id: Filter by specific court complex
        individual_court_id: Filter by specific individual court
        status: Filter by booking status (active, completed, cancelled)
    """
    # Start with base query joining through individual_court and court
    query = db.query(Booking).join(
        IndividualCourt, Booking.individual_court_id == IndividualCourt.id
    ).join(
        Court, IndividualCourt.court_id == Court.id
    ).filter(
        Court.owner_id == owner_id
    )
    
    # Apply filters
    if start_date:
        query = query.filter(Booking.booking_date >= start_date)
    
    if end_date:
        query = query.filter(Booking.booking_date <= end_date)
    
    if court_id:
        query = query.filter(Court.id == court_id)
    
    if individual_court_id:
        query = query.filter(Booking.individual_court_id == individual_court_id)
    
    if status:
        query = query.filter(Booking.status == status)
    
    # Order by booking date and start time
    query = query.order_by(Booking.booking_date.desc(), Booking.start_time)
    
    return query.all()


def get_owner_bookings_summary(db: Session, owner_id: int) -> dict:
    """
    Get summary statistics of bookings for an owner
    """
    from datetime import date
    
    today = datetime.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    # Get all bookings in last 30 days
    bookings = get_bookings_by_owner(
        db, 
        owner_id,
        start_date=datetime.combine(thirty_days_ago, datetime.min.time()),
        end_date=datetime.combine(today, datetime.max.time())
    )
    
    total_bookings = len(bookings)
    active_bookings = len([b for b in bookings if b.status == 'active'])
    completed_bookings = len([b for b in bookings if b.status == 'completed'])
    cancelled_bookings = len([b for b in bookings if b.status == 'cancelled'])
    
    return {
        "total_bookings": total_bookings,
        "active_bookings": active_bookings,
        "completed_bookings": completed_bookings,
        "cancelled_bookings": cancelled_bookings,
        "period_days": 30
    }

