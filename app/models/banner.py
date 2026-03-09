from sqlalchemy import Column, String, Text, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database import Base

class Banner(Base):
    __tablename__ = "banners"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    subtitle = Column(Text)
    image_url = Column(Text)
    badge_text = Column(String(50))
    badge_color = Column(String(20), default="#FB923C")
    button_text = Column(String(50), default="View Offer")
    link_type = Column(String(30), default="category")  # category, product, url
    link_value = Column(Text)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
