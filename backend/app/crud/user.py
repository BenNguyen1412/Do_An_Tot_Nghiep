from sqlalchemy.orm import Session
from app.models.user import User
from typing import Optional

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Tìm user theo email
    """
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Tìm user theo ID
    """
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user_data: dict) -> User:
    """
    Tạo user mới
    
    Args:
        db: Database session
        user_data: Dictionary chứa thông tin user (đã có password hash)
    
    Returns:
        User object đã tạo
    """
    db_user = User(
        email=user_data['email'],
        hashed_password=user_data['password'],  # ← ĐỔI THÀNH hashed_password
        full_name=user_data['full_name'],
        phone_number=user_data.get('phone_number'),
        role=user_data.get('role', 'user'),
        address=user_data.get('address'),
        avatar_url=user_data.get('avatar_url'),
        is_active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

def update_user(db: Session, user_id: int, user_data: dict) -> Optional[User]:
    """
    Cập nhật thông tin user
    """
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    for key, value in user_data.items():
        if hasattr(db_user, key):
            setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    """
    Xóa user
    """
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    
    return True