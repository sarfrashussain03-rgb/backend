from sqlalchemy import Column, String, Numeric, Integer, ForeignKey, Date, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    order_number = Column(String(50))
    total_amount = Column(Numeric(10, 2))
    shipping_method = Column(String(50))
    delivery_date = Column(Date)
    order_source = Column(String(50))  # e.g. 'whatsapp', 'app'
    payment_status = Column(String(50), default='pending')
    order_status = Column(String(50), default='pending')
    stripe_payment_intent_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User")
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"))
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    sku = Column(String(100))
    barcode = Column(String(100))
    quantity = Column(Integer)
    unit_price = Column(Numeric(10, 2))
    subtotal = Column(Numeric(10, 2))

    order = relationship("Order", back_populates="items")
    product = relationship("Product")
