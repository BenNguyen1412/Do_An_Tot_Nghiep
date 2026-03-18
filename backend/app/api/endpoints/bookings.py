"""
Booking endpoints with VietQR payment integration
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user, get_current_owner, get_current_admin
from app.models.user import User
from app.models.court import PaymentMethod
from app.schemas.court import (
    BookingCreate,
    Booking,
    BookingWithPayment,
    PaymentInfo,
    PaymentPreviewRequest,
    BookingUpdate
)
from app.crud import court as court_crud
from app.crud.user import get_user_by_id
from app.core.vietqr_service import VietQRService

router = APIRouter()


def calculate_multi_tier_price(start_time: str, end_time: str, time_slots: list) -> float:
    """
    Calculate price for multi-tier time slots.
    
    Similar to frontend calculation: iterate through 30-minute intervals
    and sum up prices for each interval that falls into a time slot tier.
    """
    if not time_slots:
        return 0.0
    
    from datetime import datetime as dt, timedelta
    
    # Parse times
    start_dt = dt.strptime(start_time, "%H:%M")
    end_dt = dt.strptime(end_time, "%H:%M")
    
    total_price = 0.0
    current_time = start_dt
    
    # Iterate through 30-minute intervals (0.5 hour each)
    while current_time < end_dt:
        next_time = current_time + timedelta(minutes=30)
        
        # Find which time_slot this interval belongs to
        for slot in time_slots:
            slot_start_str = slot.get("start_time", "")
            slot_end_str = slot.get("end_time", "")
            slot_price = slot.get("price", 0)
            
            slot_start = dt.strptime(slot_start_str, "%H:%M")
            slot_end = dt.strptime(slot_end_str, "%H:%M")
            
            # Check if current interval starts within this slot
            if current_time >= slot_start and current_time < slot_end:
                # Add price for this 30-minute interval (0.5 hour)
                total_price += slot_price * 0.5
                break
        
        current_time = next_time
    
    return total_price


@router.post("/payment-preview", response_model=PaymentInfo)
async def get_payment_preview(
    preview_data: PaymentPreviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate VietQR payment preview without creating a booking.

    Booking will only be created when user presses Complete on payment step.
    """
    court = court_crud.get_court(db, preview_data.court_id)
    if not court:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy thông tin sân"
        )

    available_courts = court_crud.find_available_courts(
        db,
        court.id,
        preview_data.booking_date,
        preview_data.start_time,
        preview_data.end_time,
    )

    if not available_courts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tất cả sân đã có lịch đặt trong khung giờ này. Vui lòng chọn khung giờ khác.",
        )

    owner = get_user_by_id(db, court.owner_id)
    if not owner or not owner.bank_account_number or not owner.bank_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chủ sân chưa cấu hình tài khoản ngân hàng để nhận thanh toán.",
        )

    # Calculate amount using multi-tier pricing (same as frontend)
    amount = calculate_multi_tier_price(
        preview_data.start_time,
        preview_data.end_time,
        court.time_slots or []
    )

    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể tính giá đặt sân cho khung giờ đã chọn.",
        )

    payment_content = (
        f"TMP{preview_data.court_id}-"
        f"{preview_data.booking_date.strftime('%d%m%y')}-"
        f"{preview_data.start_time.replace(':', '')}"
    )

    qr_url = VietQRService().generate_qr_url(
        bank_code=owner.bank_code,
        account_number=owner.bank_account_number,
        amount=int(amount),
        description=payment_content,
        account_name=owner.bank_account_name,
    )

    return {
        "qr_code_url": qr_url,
        "bank_name": owner.bank_name or "Ngân hàng",
        "account_number": owner.bank_account_number,
        "account_name": owner.bank_account_name or owner.full_name,
        "amount": amount,
        "content": payment_content,
        "booking_id": None,
        "expires_at": datetime.utcnow(),
    }


@router.post("/", response_model=BookingWithPayment, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new booking with payment info
    
    - For VietQR payment: generates QR code and returns payment info
    - For cash payment: booking is automatically confirmed
    """
    try:
        # Create booking with payment
        booking = court_crud.create_booking(
            db=db,
            booking=booking_data,
            user_id=current_user.id
        )
        
        # Get payment info if VietQR
        payment_info = None
        if booking.payment_method == PaymentMethod.vietqr and booking.qr_code_url:
            payment_info = court_crud.get_payment_info(db, booking.id)
        
        return {
            **booking.__dict__,
            "payment_info": payment_info
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Không thể tạo booking: {str(e)}"
        )


@router.get("/{booking_id}", response_model=Booking)
async def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get booking details by ID
    
    - User can only view their own bookings
    - Owner can view bookings for their courts
    - Admin can view all bookings
    """
    booking = court_crud.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy booking"
        )
    
    # Check permissions
    if current_user.role == "user" and booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xem booking này"
        )
    
    # If owner, check if booking belongs to their court
    if current_user.role == "owner":
        individual_court = court_crud.get_individual_court(db, booking.individual_court_id)
        if not individual_court:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy sân")
        
        parent_court = court_crud.get_court(db, individual_court.court_id)
        if not parent_court or parent_court.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền xem booking này"
            )
    
    return booking


@router.get("/{booking_id}/payment-info", response_model=PaymentInfo)
async def get_booking_payment_info(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get payment information for a booking (QR code, bank details, etc.)
    """
    booking = court_crud.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy booking"
        )
    
    # Check permissions
    if current_user.role == "user" and booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xem thông tin thanh toán này"
        )
    
    payment_info = court_crud.get_payment_info(db, booking_id)
    if not payment_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy thông tin thanh toán"
        )
    
    return payment_info


@router.post("/{booking_id}/verify-payment", response_model=Booking)
async def verify_payment(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Verify payment for a booking (checks bank transactions)
    
    - User can request auto-verification
    - System checks bank API for matching transaction
    """
    booking = court_crud.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy booking"
        )
    
    # Check permissions
    if current_user.role == "user" and booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền verify booking này"
        )
    
    # Auto-verify payment
    verified_booking = await court_crud.auto_verify_booking_payment(db, booking_id)
    
    if not verified_booking:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không tìm thấy giao dịch thanh toán. Vui lòng kiểm tra lại hoặc liên hệ chủ sân."
        )
    
    return verified_booking


@router.post("/{booking_id}/manual-verify", response_model=Booking)
async def manual_verify_payment(
    booking_id: int,
    transaction_id: str,
    note: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_owner)  # Only owner/admin can manually verify
):
    """
    Manually verify payment for a booking (owner/admin action)
    
    - Owner can manually confirm payment after checking their bank account
    - Requires bank transaction ID
    """
    booking = court_crud.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy booking"
        )
    
    # Check if owner owns the court
    individual_court = court_crud.get_individual_court(db, booking.individual_court_id)
    if not individual_court:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy sân")
    
    parent_court = court_crud.get_court(db, individual_court.court_id)
    if not parent_court:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy sân")
    
    # Only owner of the court or admin can manually verify
    if current_user.role == "owner" and parent_court.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền verify booking này"
        )
    
    # Manually verify
    verified_booking = court_crud.manual_verify_booking_payment(
        db=db,
        booking_id=booking_id,
        transaction_id=transaction_id,
        note=note
    )
    
    return verified_booking


@router.post("/{booking_id}/confirm-payment", response_model=Booking)
async def confirm_payment(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_owner)  # Only owner can confirm
):
    """
    Owner confirms they received payment and activates the booking
    
    - Owner checks their bank account and confirms payment manually
    - Changes booking status from 'pending' to 'active'
    """
    booking = court_crud.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy booking"
        )
    
    # Check if booking is in pending status
    if booking.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Booking đang ở trạng thái '{booking.status}', không thể xác nhận"
        )
    
    # Check if owner owns the court
    individual_court = court_crud.get_individual_court(db, booking.individual_court_id)
    if not individual_court:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy sân")
    
    parent_court = court_crud.get_court(db, individual_court.court_id)
    if not parent_court:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy sân")
    
    # Only owner of the court can confirm
    if parent_court.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xác nhận booking này"
        )
    
    # Update booking status to active
    booking.status = "active"
    booking.payment_verified = True
    booking.verified_at = datetime.utcnow()
    db.commit()
    db.refresh(booking)
    
    return booking


@router.get("/user/my-bookings", response_model=List[Booking])
async def get_my_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all bookings for current user
    """
    bookings = court_crud.get_bookings_by_user(db, current_user.id)
    return bookings


@router.put("/{booking_id}", response_model=Booking)
async def update_booking(
    booking_id: int,
    booking_update: BookingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update booking (change status, etc.)
    
    - User can cancel their own bookings
    - Owner can update booking status for their courts
    """
    booking = court_crud.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy booking"
        )
    
    # Check permissions
    if current_user.role == "user":
        if booking.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền cập nhật booking này"
            )
        # Users can only cancel their bookings
        if booking_update.status and booking_update.status != "cancelled":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn chỉ có thể hủy booking"
            )
    
    if current_user.role == "owner":
        individual_court = court_crud.get_individual_court(db, booking.individual_court_id)
        if not individual_court:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy sân")
        
        parent_court = court_crud.get_court(db, individual_court.court_id)
        if not parent_court or parent_court.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền cập nhật booking này"
            )
    
    try:
        updated_booking = court_crud.update_booking(db, booking_id, booking_update)
        return updated_booking
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
