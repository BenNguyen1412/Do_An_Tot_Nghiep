from sqlalchemy.orm import Session
from typing import Optional, List
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
    
    # Convert time_slots if present
    if "time_slots" in update_data and update_data["time_slots"]:
        update_data["time_slots"] = [slot.model_dump() for slot in update_data["time_slots"]]
    
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


def create_booking(db: Session, booking: BookingCreate, user_id: int) -> Booking:
    """Create a new booking"""
    db_booking = Booking(
        individual_court_id=booking.individual_court_id,
        user_id=user_id,
        booking_date=booking.booking_date,
        start_time=booking.start_time,
        end_time=booking.end_time,
        phone_number=booking.phone_number,
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
