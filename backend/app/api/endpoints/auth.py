from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token
from app.crud import user as crud_user
from app.models.user import User

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Kiểm tra email đã tồn tại
    existing_user = crud_user.get_user_by_email(db, email=user_data.email)
    if existing_user:
        print(f"❌ Email đã tồn tại: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã được đăng ký"
        )
    
    # Hash mật khẩu
    hashed_password = get_password_hash(user_data.password)
    
    # Tạo user mới với mật khẩu đã hash
    user_data_dict = user_data.model_dump()
    user_data_dict['password'] = hashed_password
    
    # Tạo user trong database
    db_user = crud_user.create_user(db, user_data_dict)
    
    return db_user

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    print(f"🔑 Login attempt: {user_credentials.email}")
    
    # Tìm user theo email
    user = crud_user.get_user_by_email(db, email=user_credentials.email)
    
    if not user:
        print(f"❌ User không tồn tại: {user_credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không đúng",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify mật khẩu
    if not verify_password(user_credentials.password, user.hashed_password):
        print(f"❌ Sai mật khẩu cho: {user_credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không đúng",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Tạo access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id, "role": user.role},
        expires_delta=access_token_expires
    )
    
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }