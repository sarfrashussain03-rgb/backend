from sqlalchemy import Column, String, Text, Boolean, ForeignKey, Numeric, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"))
    name = Column(String(255), nullable=False)
    sku = Column(String(100), unique=True)
    barcode = Column(String(100))
    description = Column(Text)
    base_unit = Column(String(50))
    weight = Column(String(50))
    is_halal = Column(Boolean, default=True)
    status = Column(String(20), default="active")
    badge = Column(String(30))               # BESTSELLER, HOT, NEW, PROMO
    original_price = Column(Numeric(10, 2))  # for strikethrough display
    packaging = Column(Text)                 # e.g. "24 packs per carton"
    moq_text = Column(String(100))           # min order qty label
    is_popular = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    brand = Column(String(100))

    category = relationship("Category", back_populates="products")
    images = relationship("ProductImage", back_populates="product", order_by="ProductImage.sort_order")
    inventory = relationship("Inventory", uselist=False, back_populates="product")
    tier_pricing = relationship("ProductTierPricing", back_populates="product", order_by="ProductTierPricing.min_qty")