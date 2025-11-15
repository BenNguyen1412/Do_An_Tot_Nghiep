from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core.database import get_db
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.crud import user as crud_user

router = APIRouter()


@router.post("/signup", response_model=TokenResponse)
def signup(user_create: UserCreate, db: Session = Depends(get_db)):
    """
    Register new user
    """
    # Check if user already exists
    existing_user = crud_user.get_user_by_email(db, email=user_create.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã được đăng ký"
        )
    
    # Create new user
    user = crud_user.create_user(db, user_create)
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role.value}
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.from_orm(user)
    )


@router.post("/login", response_model=TokenResponse)
def login(user_login: UserLogin, db: Session = Depends(get_db)):
    """
    Login user
    """
    # Authenticate user
    user = crud_user.authenticate_user(
        db, 
        email=user_login.email, 
        password=user_login.password,
        role=user_login.role
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email, mật khẩu hoặc loại tài khoản không đúng"
        )
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role.value}
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.from_orm(user)
    )


@router.post("/refresh")
def refresh_token(
    refresh_token: str = Body(..., embed=True),  # ← FIX: Nhận body đúng format
    db: Session = Depends(get_db)
):
    """
    Refresh access token
    """
    payload = decode_token(refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = int(payload.get("sub"))
    user = crud_user.get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Create new access token
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role.value}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
def logout():
    """
    Logout user (client should remove tokens)
    """
    return {"message": "Successfully logged out"}