from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class UserBase(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

class UserUpdate(UserBase):
    pass

class UserSchema(UserBase):
    id: UUID
    role: str
    account_status: str
    is_active: bool

    class Config:
        from_attributes = True
