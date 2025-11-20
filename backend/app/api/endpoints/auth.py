from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, create_access_token, get_password_hash
from app.models.user import User
from app.schemas.user import UserLogin, UserRegister, Token

router = APIRouter()

@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login endpoint"""
    
    # Clean email
    email = user_data.email.strip().lower()
    
    print(f"🔐 LOGIN ATTEMPT:")
    print(f"   Email: {email}")
    
    # Find user
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        print(f"❌ User not found: {email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email không tồn tại trong hệ thống"
        )
    
    print(f"✅ User found: {user.email}")
    
    # Verify password
    if not verify_password(user_data.password, user.hashed_password):
        print(f"❌ Wrong password")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Mật khẩu không chính xác"
        )
    
    print(f"✅ Password correct")
    
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
    """Register endpoint"""
    
    # Clean email
    email = user_data.email.strip().lower()
    
    print(f"📝 REGISTER ATTEMPT:")
    print(f"   Email: {email}")
    print(f"   Full name: {user_data.full_name}")
    print(f"   Role: {user_data.role}")
    
    # Check if email exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        print(f"❌ Email already exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã được đăng ký. Vui lòng sử dụng email khác."
        )
    
    # Create new user
    new_user = User(
        email=email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        phone_number=user_data.phone_number,
        role=user_data.role,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    print(f"✅ User created: {new_user.email}")
    
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