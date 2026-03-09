from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    auth_uid = Column(String(255), nullable=False)
    name = Column(String(255))
    email = Column(String(255))
    phone = Column(String(255))
    role = Column(String(50), default="wholesale_user")
    account_status = Column(String(50), default="pending")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
