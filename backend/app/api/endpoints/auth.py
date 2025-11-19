from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.schemas.user import UserLogin, UserRegister, UserResponse, Token
from app.crud import user as crud_user

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Đăng ký tài khoản mới
    """
    print(f"📝 Register attempt: {user_data.email}")
    
    # Kiểm tra email đã tồn tại chưa
    existing_user = crud_user.get_user_by_email(db, email=user_data.email)
    if existing_user:
        print(f"❌ Email already exists: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã được sử dụng"
        )
    
    # Tạo user mới (CRUD sẽ tự hash password)
    user = crud_user.create_user(db, user_data)
    print(f"✅ User created successfully: {user.email}")
    
    return user

@router.post("/login", response_model=Token)
async def login(user_login: UserLogin, db: Session = Depends(get_db)):
    """
    Đăng nhập
    """
    print(f"🔑 Login attempt: {user_login.email}")
    
    # Kiểm tra user có tồn tại không
    user = crud_user.get_user_by_email(db, email=user_login.email)
    if not user:
        print(f"❌ User không tồn tại: {user_login.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác"
        )
    
    # Kiểm tra mật khẩu
    if not verify_password(user_login.password, user.hashed_password):
        print(f"❌ Sai mật khẩu cho user: {user_login.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác"
        )
    
    print(f"✅ Login successful: {user.email}")
    
    # Tạo access token
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }