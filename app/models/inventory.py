from sqlalchemy import Column, Integer, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

class Inventory(Base):
    __tablename__ = "inventory"

    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), primary_key=True)
    stock_quantity = Column(Integer, default=0)
    restock_date = Column(Date)

    product = relationship("Product", back_populates="inventory")