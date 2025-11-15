from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole


class UserCreate(UserBase):
    password: str
    phone_number: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str
    role: UserRole


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    avatar_url: Optional[str] = None


class UserResponse(UserBase):
    id: int
    phone_number: Optional[str] = None
    address: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class UserListResponse(BaseModel):
    """Response for list of users"""
    total: int
    users: List[UserResponse]