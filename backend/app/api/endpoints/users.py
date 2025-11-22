from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.user import UserResponse, UserListResponse, UserUpdate
from app.crud import user as crud_user

router = APIRouter()

@router.get("/", response_model=UserListResponse)
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách users với phân trang (không bao gồm admin)
    """
    # Lọc bỏ users có role = 'admin'
    users = db.query(crud_user.User).filter(crud_user.User.role != 'admin').offset(skip).limit(limit).all()
    total = db.query(crud_user.User).filter(crud_user.User.role != 'admin').count()
    
    return {
        "users": users,
        "total": total
    }

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Lấy thông tin user theo ID
    """
    user = crud_user.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User không tồn tại"
        )
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
):
    """
    Cập nhật thông tin user
    """
    # Kiểm tra user có tồn tại không
    existing_user = crud_user.get_user_by_id(db, user_id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User không tồn tại"
        )
    
    # Chỉ update các field không None
    update_data = user_data.model_dump(exclude_unset=True)
    
    # Nếu update email, kiểm tra email đã tồn tại chưa (trừ email của chính user đó)
    if 'email' in update_data:
        email_check = crud_user.get_user_by_email(db, update_data['email'])
        if email_check and email_check.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email đã được sử dụng bởi tài khoản khác"
            )
    
    user = crud_user.update_user(db, user_id, update_data)
    return user

@router.delete("/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Xóa user
    """
    success = crud_user.delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User không tồn tại"
        )
    return {"message": "Xóa user thành công"}

@router.post("/test-hash")
async def test_password_hash(password: str):
    """
    Endpoint test để kiểm tra password hashing
    """
    from app.core.security import get_password_hash, verify_password
    
    hashed = get_password_hash(password)
    
    return {
        "original_password": password,
        "hashed_password": hashed,
        "hash_length": len(hashed),
        "is_bcrypt_format": hashed.startswith("$2b$"),
        "verify_result": verify_password(password, hashed),
        "info": {
            "algorithm": "bcrypt",
            "cost_factor": "12 (default)",
            "note": "Mỗi lần hash sẽ tạo ra kết quả khác nhau do salt ngẫu nhiên"
        }
    }