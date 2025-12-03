from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.notification import (
    Notification,
    NotificationCreate,
    CourtRequest,
    CourtRequestCreate,
    CourtRequestUpdate,
)
from app.crud import notification as notification_crud
from app.crud import court as court_crud
import json
import os
import uuid
from pathlib import Path

router = APIRouter()


# Image upload endpoint
@router.post("/upload-images")
async def upload_images(
    images: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
):
    """Upload images and return URLs (owner only)"""
    if current_user.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners can upload images",
        )
    
    # Create uploads directory if it doesn't exist
    upload_dir = Path("uploads/courts")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    image_urls = []
    for image in images:
        # Generate unique filename
        file_ext = os.path.splitext(image.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = upload_dir / unique_filename
        
        # Save file
        with open(file_path, "wb") as f:
            content = await image.read()
            f.write(content)
        
        # Generate URL (relative path from backend root)
        image_url = f"/uploads/courts/{unique_filename}"
        image_urls.append(image_url)
    
    return {"urls": image_urls}


# Notification endpoints
@router.get("/notifications", response_model=List[Notification])
async def get_my_notifications(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all notifications for current user"""
    return notification_crud.get_user_notifications(db, current_user.id, skip, limit)


@router.get("/notifications/unread-count")
async def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get count of unread notifications"""
    count = notification_crud.get_unread_count(db, current_user.id)
    return {"count": count}


@router.put("/notifications/{notification_id}/read", response_model=Notification)
async def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a notification as read"""
    notification = notification_crud.mark_as_read(db, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    # Verify ownership
    if notification.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return notification


@router.post("/notifications/mark-all-read")
async def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark all notifications as read"""
    notification_crud.mark_all_as_read(db, current_user.id)
    return {"message": "All notifications marked as read"}


# Court Request endpoints
@router.post("/court-requests", response_model=CourtRequest, status_code=status.HTTP_201_CREATED)
async def create_court_request(
    request: CourtRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new court registration request (owner only)"""
    if current_user.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners can submit court requests",
        )
    
    # Create court request
    db_request = notification_crud.create_court_request(db, request, current_user.id)
    
    # Create notification for all admins
    from app.crud.user import get_users_by_role
    admins = get_users_by_role(db, "admin")
    
    for admin in admins:
        notification = NotificationCreate(
            user_id=admin.id,
            title="Yêu cầu đăng sân mới",
            message=f"{current_user.full_name} đã gửi yêu cầu đăng sân '{request.name}'",
            type="request_created",
            related_id=db_request.id,
        )
        notification_crud.create_notification(db, notification)
    
    return db_request


@router.get("/court-requests", response_model=List[CourtRequest])
async def list_court_requests(
    status_filter: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List court requests (admin sees all, owner sees only their own)"""
    if current_user.role == "admin":
        return notification_crud.get_all_court_requests(db, status_filter)
    elif current_user.role == "owner":
        return notification_crud.get_owner_court_requests(db, current_user.id)
    else:
        raise HTTPException(status_code=403, detail="Not authorized")


@router.get("/court-requests/{request_id}", response_model=CourtRequest)
async def get_court_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific court request"""
    request = notification_crud.get_court_request(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Court request not found")
    
    # Check authorization
    if current_user.role != "admin" and request.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return request


@router.put("/court-requests/{request_id}", response_model=CourtRequest)
async def update_court_request_status(
    request_id: int,
    update: CourtRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Approve or reject a court request (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can review requests")
    
    request = notification_crud.get_court_request(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Court request not found")
    
    if request.status != "pending":
        raise HTTPException(status_code=400, detail="Request already reviewed")
    
    # Update request status
    updated_request = notification_crud.update_court_request_status(
        db, request_id, update, current_user.id
    )
    
    # If approved, create the actual court
    if update.status == "approved":
        from app.schemas.court import CourtCreate, TimeSlot
        
        # Parse JSON fields
        facilities = json.loads(request.facilities) if request.facilities else []
        images = json.loads(request.images) if request.images else []
        time_slots_data = json.loads(request.time_slots) if request.time_slots else []
        time_slots = [TimeSlot(**slot) for slot in time_slots_data]
        
        # Create court
        court_data = CourtCreate(
            name=request.name,
            address=request.address,
            district=request.district,
            city=request.city,
            description=request.description,
            court_quantity=request.court_quantity,
            opening_time=request.opening_time,
            closing_time=request.closing_time,
            facilities=facilities,
            contact_phone=request.contact_phone,
            contact_email=request.contact_email,
            time_slots=time_slots,
        )
        
        court = court_crud.create_court(db, court_data, request.owner_id, images)
        
        # Create notification for owner
        notification = NotificationCreate(
            user_id=request.owner_id,
            title="Yêu cầu đăng sân được duyệt",
            message=f"Yêu cầu đăng sân '{request.name}' của bạn đã được phê duyệt!",
            type="request_approved",
            related_id=court.id,
        )
    else:
        # Create rejection notification for owner
        notification = NotificationCreate(
            user_id=request.owner_id,
            title="Yêu cầu đăng sân bị từ chối",
            message=f"Yêu cầu đăng sân '{request.name}' bị từ chối. Lý do: {update.rejection_reason or 'Không rõ'}",
            type="request_rejected",
            related_id=request_id,
        )
    
    notification_crud.create_notification(db, notification)
    
    return updated_request


@router.delete("/court-requests/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_court_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a court request (owner can delete own pending requests, admin can delete any)"""
    request = notification_crud.get_court_request(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Court request not found")
    
    # Check authorization
    if current_user.role != "admin" and request.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Owner can only delete pending requests
    if current_user.role == "owner" and request.status != "pending":
        raise HTTPException(status_code=400, detail="Cannot delete reviewed request")
    
    notification_crud.delete_court_request(db, request_id)
