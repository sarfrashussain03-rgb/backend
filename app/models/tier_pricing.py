from sqlalchemy import Column, Integer, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base

class ProductTierPricing(Base):
    __tablename__ = "product_tier_pricing"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    min_qty = Column(Integer)
    max_qty = Column(Integer)
    unit_price = Column(Numeric(10,2))

    product = relationship("Product", back_populates="tier_pricing")