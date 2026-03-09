from sqlalchemy import Column, String, Text, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(150), nullable=False)
    description = Column(Text)
    image_url = Column(Text)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"))
    is_active = Column(Boolean, default=True)
    malay_name = Column(String(150))
    sort_order = Column(Integer, default=0)
    icon = Column(String(50))           # emoji or icon name
    product_count = Column(Integer, default=0)

    products = relationship("Product", back_populates="category")
    parent = relationship("Category", remote_side=[id])