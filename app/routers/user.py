from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.database import SessionLocal
from app.models.user import User
from app.schemas.user import UserSchema, UserUpdate
from app.core.auth import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["Users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/me", response_model=UserSchema)
def get_me(current_user: User = Depends(get_current_user)):
    """Get profile of the currently logged-in user."""
    return current_user

@router.put("/me", response_model=UserSchema)
def update_me(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update profile of the currently logged-in user."""
    if user_data.name is not None:
        current_user.name = user_data.name
    if user_data.email is not None:
        current_user.email = user_data.email
    if user_data.phone is not None:
        current_user.phone = user_data.phone
    
    db.commit()
    db.refresh(current_user)
    return current_user

class SyncUserRequest(BaseModel):
    auth_uid: str
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

@router.post("/sync", response_model=UserSchema)
def sync_user(
    data: SyncUserRequest,
    db: Session = Depends(get_db)
):
    """
    Sync Supabase user with local DB.
    Called after signup/login from the frontend.
    Creates user if not found; updates name/email/phone on signup.
    """
    user = db.query(User).filter(User.auth_uid == data.auth_uid).first()
    if not user:
        # New user: create with all provided details
        user = User(
            auth_uid=data.auth_uid,
            name=data.name,
            email=data.email,
            phone=data.phone,
            account_status="active"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Existing user: only update fields that are provided
        changed = False
        if data.name and not user.name:
            user.name = data.name
            changed = True
        if data.email and not user.email:
            user.email = data.email
            changed = True
        if data.phone and not user.phone:
            user.phone = data.phone
            changed = True
        if changed:
            db.commit()
            db.refresh(user)
    return user
