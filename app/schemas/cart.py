from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal

class CartItemBase(BaseModel):
    product_id: UUID
    quantity: int

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: int

class CartItem(CartItemBase):
    id: UUID
    cart_id: UUID
    unit_price_snapshot: Optional[Decimal]
    
    class Config:
        from_attributes = True

class Cart(BaseModel):
    id: UUID
    user_id: Optional[UUID]
    updated_at: datetime
    items: List[CartItem]

    class Config:
        from_attributes = True
