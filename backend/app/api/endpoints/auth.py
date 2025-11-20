from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, create_access_token, get_password_hash
from app.models.user import User
from app.schemas.user import UserLogin, UserRegister, Token

router = APIRouter()

@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    
    # Clean email
    email = user_data.email.strip().lower()
    
    # Find user
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        print(f"❌ User not found: {email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email không tồn tại"  
        )
    
    # Verify password
    if not verify_password(user_data.password, user.hashed_password):
        print(f"❌ Wrong password")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Mật khẩu không chính xác" 
        )
    
    # Check if active
    if not user.is_active:
        print(f"❌ Account inactive")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị khóa"
        )
    
    # Create token
    access_token = create_access_token(data={"sub": user.email})
    
    print(f"✅ Login successful")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "phone_number": user.phone_number,
            "is_active": user.is_active
        }
    }

@router.post("/register", response_model=Token)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register new user"""
    
    # Clean email
    email = user_data.email.strip().lower()
    # Check if email exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        print(f"❌ Email already exists: {email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã được đăng ký. Vui lòng sử dụng email khác."
        )
    
    # Validate role
    valid_roles = ['user', 'owner', 'enterprise']
    if user_data.role not in valid_roles:
        print(f"❌ Invalid role: {user_data.role}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role không hợp lệ. Chỉ chấp nhận: {', '.join(valid_roles)}"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    
    new_user = User(
        email=email,
        hashed_password=hashed_password,
        full_name=user_data.full_name.strip(),
        phone_number=user_data.phone_number.strip() if user_data.phone_number else None,
        role=user_data.role,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create token
    access_token = create_access_token(data={"sub": new_user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "full_name": new_user.full_name,
            "role": new_user.role,
            "phone_number": new_user.phone_number,
            "is_active": new_user.is_active
        }
    }