from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import uuid as uuid_pkg
from datetime import datetime

from app.database import SessionLocal
from app.models.order import Order, OrderItem
from app.models.user import User
from app.models.product import Product
from app.schemas.order import OrderCreate, Order as OrderSchema, OrderList
from app.core.auth import get_current_user

router = APIRouter(prefix="/orders", tags=["Orders"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[OrderList])
def get_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all orders for the current user."""
    orders = db.query(Order).filter(Order.user_id == current_user.id).order_by(Order.created_at.desc()).all()
    return orders

@router.get("/{order_id}", response_model=OrderSchema)
def get_order(
    order_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific order for the current user."""
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.post("/", response_model=OrderSchema)
def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new order."""
    # Generate a simple order number
    order_num = f"ORD-{datetime.now().strftime('%Y%m%d')}-{str(uuid_pkg.uuid4())[:8].upper()}"
    
    total_amount = 0
    for item in order_data.items:
        total_amount += item.unit_price * item.quantity

    new_order = Order(
        user_id=current_user.id,
        order_number=order_num,
        total_amount=total_amount,
        shipping_method=order_data.shipping_method,
        delivery_date=order_data.delivery_date,
        order_source=order_data.order_source,
        stripe_payment_intent_id=order_data.stripe_payment_intent_id,
        # If stripe PI ID is provided, mark as paid (client-side trust for test mode)
        # In production, the webhook should be the source of truth
        payment_status="paid" if order_data.stripe_payment_intent_id else "pending",
        order_status="confirmed" if order_data.stripe_payment_intent_id else "pending"
    )
    
    db.add(new_order)
    db.flush() # To get the new_order.id
    
    for item in order_data.items:
        # Fetch product details if needed (sku, barcode)
        product = db.query(Product).filter(Product.id == item.product_id).first()
        
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item.product_id,
            sku=product.sku if product else None,
            barcode=product.barcode if product else None,
            quantity=item.quantity,
            unit_price=item.unit_price,
            subtotal=item.unit_price * item.quantity
        )
        db.add(order_item)
    
    db.commit()
    db.refresh(new_order)
    return new_order
