from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.user import UserResponse, UserListResponse, UserUpdate
from app.crud import user as crud_user
from app.models.user import UserRole

router = APIRouter()


@router.get("/", response_model=UserListResponse)
def get_all_users(
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    Get list of all users with pagination
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum records to return (default: 100, max: 100)
    
    Returns total count and list of users
    """
    users = crud_user.get_users(db, skip=skip, limit=limit)
    total = crud_user.get_users_count(db)
    
    return UserListResponse(
        total=total,
        users=[UserResponse.from_orm(user) for user in users]
    )


@router.get("/stats", response_model=dict)
def get_users_stats(db: Session = Depends(get_db)):
    """
    Get user statistics
    
    Returns:
    - total: Total number of users
    - by_role: Count grouped by role (user, enterprise, owner)
    """
    from sqlalchemy import func
    from app.models.user import User
    
    total = db.query(func.count(User.id)).scalar()
    
    # Count by role
    role_counts = db.query(
        User.role,
        func.count(User.id)
    ).group_by(User.role).all()
    
    return {
        "total": total,
        "by_role": {role.value: count for role, count in role_counts}
    }


@router.get("/by-role/{role}", response_model=List[UserResponse])
def get_users_by_role(
    role: UserRole,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get users filtered by role
    
    - **role**: user, enterprise, or owner
    - **skip**: Number of records to skip
    - **limit**: Maximum records to return
    """
    users = crud_user.get_users_by_role(db, role=role, skip=skip, limit=limit)
    return [UserResponse.from_orm(user) for user in users]


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get user by ID
    
    - **user_id**: User ID to retrieve
    
    Returns user details
    """
    user = crud_user.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse.from_orm(user)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    """
    Update user information
    
    - **user_id**: User ID to update
    - **user_update**: Fields to update (all optional):
        - full_name
        - phone_number
        - address
        - avatar_url
    
    Returns updated user details
    """
    user = crud_user.update_user(db, user_id, user_update)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse.from_orm(user)


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete user by ID
    
    - **user_id**: User ID to delete
    
    Returns success message
    """
    success = crud_user.delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {
        "message": "User deleted successfully",
        "user_id": user_id
    }