"""
Booking endpoints with VietQR payment integration
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user, get_current_owner
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
from app.core.booking_qr_service import (
    generate_booking_access_token,
    decode_booking_access_token,
    build_booking_info_url,
    build_qr_image_url,
    build_booking_info_html,
)
from app.core.email_service import send_booking_qr_email

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
    booking.booking_status = "active"
    booking.payment_status = "paid"
    booking.payment_verified_at = datetime.utcnow()
    db.commit()
    db.refresh(booking)

    # Build and send booking info QR email to customer.
    # Keep confirm successful even if email fails, but persist the result for UI/debugging.
    customer = get_user_by_id(db, booking.user_id)
    customer_email = booking.customer_email or (customer.email if customer else None)
    customer_name = booking.customer_name or (customer.full_name if customer else "Khách hàng")

    individual_court = court_crud.get_individual_court(db, booking.individual_court_id)
    parent_court = court_crud.get_court(db, individual_court.court_id) if individual_court else None

    if customer_email and individual_court and parent_court:
        token = generate_booking_access_token(booking.id)
        booking_info_url = build_booking_info_url(token)
        qr_image_url = build_qr_image_url(booking_info_url)

        booking_date_str = booking.booking_date.strftime("%d/%m/%Y") if booking.booking_date else "N/A"
        total_price_str = f"{int(float(booking.total_price or 0)):,}".replace(",", ".")

        sent_ok, sent_msg = send_booking_qr_email(
            to_email=customer_email,
            customer_name=customer_name,
            booking_id=booking.id,
            qr_image_url=qr_image_url,
            booking_info_url=booking_info_url,
            court_name=parent_court.name,
            individual_court_name=individual_court.name,
            booking_date=booking_date_str,
            start_time=booking.start_time,
            end_time=booking.end_time,
            total_price=total_price_str,
        )

        booking.payment_note = f"EMAIL_SENT: {sent_msg}" if sent_ok else f"EMAIL_FAILED: {sent_msg}"
    else:
        booking.payment_note = "EMAIL_FAILED: Missing customer email or court information"

    db.commit()
    db.refresh(booking)
    
    return booking


@router.get("/qr-booking/{token}", response_class=HTMLResponse, include_in_schema=False)
async def view_booking_from_qr(
    token: str,
    db: Session = Depends(get_db),
):
    """Public booking details page opened when customer scans QR from email."""
    booking_id = decode_booking_access_token(token)
    if not booking_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired QR code"
        )

    booking = court_crud.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )

    customer = get_user_by_id(db, booking.user_id)
    individual_court = court_crud.get_individual_court(db, booking.individual_court_id)
    parent_court = court_crud.get_court(db, individual_court.court_id) if individual_court else None
    owner = get_user_by_id(db, parent_court.owner_id) if parent_court else None

    booking_date_str = booking.booking_date.strftime("%d/%m/%Y") if booking.booking_date else "N/A"
    total_price_str = f"{int(float(booking.total_price or 0)):,}".replace(",", ".")

    html = build_booking_info_html(
        booking_id=booking.id,
        customer_name=booking.customer_name or (customer.full_name if customer else "N/A"),
        customer_email=booking.customer_email or (customer.email if customer else "N/A"),
        phone_number=booking.phone_number or (customer.phone_number if customer else "N/A"),
        booking_date=booking_date_str,
        start_time=booking.start_time,
        end_time=booking.end_time,
        total_price=total_price_str,
        court_name=parent_court.name if parent_court else "N/A",
        individual_court_name=individual_court.name if individual_court else "N/A",
        owner_name=owner.full_name if owner else "N/A",
        owner_phone=owner.phone_number if owner and owner.phone_number else "N/A",
    )

    return HTMLResponse(content=html)


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
