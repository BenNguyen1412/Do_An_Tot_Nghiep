from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.court import (
    Court,
    CourtCreate,
    CourtUpdate,
    CourtWithIndividualCourts,
    IndividualCourt,
    IndividualCourtUpdate,
    IndividualCourtWithBookings,
    Booking,
    BookingCreate,
    BookingUpdate,
)
from app.crud import court as court_crud

router = APIRouter()

# Court endpoints
@router.post("/courts", response_model=Court, status_code=status.HTTP_201_CREATED)
async def create_court(
    court_data: str = Form(...),
    images: List[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new court (owner only)"""
    if current_user.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners can create courts",
        )
    
    # Parse court data from JSON string
    court_dict = json.loads(court_data)
    court = CourtCreate(**court_dict)
    
    # TODO: Handle image uploads to storage (S3, local, etc.)
    image_urls = []
    if images:
        for image in images:
            # Save image and get URL
            # image_url = save_image(image)
            # image_urls.append(image_url)
            pass
    
    db_court = court_crud.create_court(db, court, current_user.id, image_urls)
    return db_court


@router.get("/courts", response_model=List[Court])
async def list_courts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List all courts"""
    courts = court_crud.get_courts(db, skip=skip, limit=limit)
    return courts


@router.get("/courts/my", response_model=List[CourtWithIndividualCourts])
async def list_my_courts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List courts owned by the current user"""
    if current_user.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners can access this endpoint",
        )
    
    courts = court_crud.get_courts_by_owner(db, current_user.id)
    return courts


@router.get("/courts/{court_id}", response_model=CourtWithIndividualCourts)
async def get_court(
    court_id: int,
    db: Session = Depends(get_db),
):
    """Get a specific court by ID"""
    court = court_crud.get_court(db, court_id)
    if not court:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Court not found",
        )
    return court


@router.put("/courts/{court_id}", response_model=Court)
async def update_court(
    court_id: int,
    court_update: CourtUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a court (owner only)"""
    court = court_crud.get_court(db, court_id)
    if not court:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Court not found",
        )
    
    if court.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this court",
        )
    
    updated_court = court_crud.update_court(db, court_id, court_update)
    return updated_court


@router.delete("/courts/{court_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_court(
    court_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a court (owner or admin only)"""
    court = court_crud.get_court(db, court_id)
    if not court:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Court not found",
        )
    
    if court.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this court",
        )
    
    court_crud.delete_court(db, court_id)


# Individual Court endpoints
@router.get("/courts/{court_id}/individual-courts", response_model=List[IndividualCourtWithBookings])
async def list_individual_courts(
    court_id: int,
    db: Session = Depends(get_db),
):
    """List all individual courts for a specific court"""
    court = court_crud.get_court(db, court_id)
    if not court:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Court not found",
        )
    
    individual_courts = court_crud.get_individual_courts_by_court(db, court_id)
    return individual_courts


@router.put("/individual-courts/{individual_court_id}", response_model=IndividualCourt)
async def update_individual_court(
    individual_court_id: int,
    individual_court_update: IndividualCourtUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an individual court (owner only)"""
    individual_court = court_crud.get_individual_court(db, individual_court_id)
    if not individual_court:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Individual court not found",
        )
    
    # Check ownership
    court = court_crud.get_court(db, individual_court.court_id)
    if court.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this individual court",
        )
    
    updated_individual_court = court_crud.update_individual_court(
        db, individual_court_id, individual_court_update
    )
    return updated_individual_court


# Booking endpoints
@router.post("/bookings", response_model=Booking, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new booking"""
    # Check if individual court exists
    individual_court = court_crud.get_individual_court(db, booking.individual_court_id)
    if not individual_court:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Individual court not found",
        )
    
    # TODO: Add validation for overlapping bookings
    
    db_booking = court_crud.create_booking(db, booking, current_user.id)
    return db_booking


@router.get("/bookings/my", response_model=List[Booking])
async def list_my_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List bookings for the current user"""
    bookings = court_crud.get_bookings_by_user(db, current_user.id)
    return bookings


@router.put("/bookings/{booking_id}", response_model=Booking)
async def update_booking(
    booking_id: int,
    booking_update: BookingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a booking"""
    booking = court_crud.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )
    
    # Only the booking owner or court owner can update
    individual_court = court_crud.get_individual_court(db, booking.individual_court_id)
    court = court_crud.get_court(db, individual_court.court_id)
    
    if booking.user_id != current_user.id and court.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this booking",
        )
    
    updated_booking = court_crud.update_booking(db, booking_id, booking_update)
    return updated_booking


@router.delete("/bookings/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a booking"""
    booking = court_crud.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )
    
    # Only the booking owner or court owner can delete
    individual_court = court_crud.get_individual_court(db, booking.individual_court_id)
    court = court_crud.get_court(db, individual_court.court_id)
    
    if booking.user_id != current_user.id and court.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this booking",
        )
    
    court_crud.delete_booking(db, booking_id)
