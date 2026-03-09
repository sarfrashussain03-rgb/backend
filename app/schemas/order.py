from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal

class OrderItemBase(BaseModel):
    product_id: UUID
    quantity: int
    unit_price: Decimal

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: UUID
    sku: Optional[str]
    barcode: Optional[str]
    subtotal: Decimal

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    shipping_method: Optional[str] = None
    delivery_date: Optional[datetime] = None
    order_source: Optional[str] = "app"

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]
    stripe_payment_intent_id: Optional[str] = None

class Order(OrderBase):
    id: UUID
    user_id: UUID
    order_number: str
    total_amount: Decimal
    payment_status: str
    order_status: str
    stripe_payment_intent_id: Optional[str] = None
    created_at: datetime
    items: List[OrderItem]

    class Config:
        from_attributes = True

class OrderList(BaseModel):
    id: UUID
    order_number: str
    total_amount: Decimal
    order_status: str
    created_at: datetime

    class Config:
        from_attributes = True
