from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import SessionLocal
from app.models.cart import Cart, CartItem
from app.models.user import User
from app.models.product import Product
from app.schemas.cart import Cart as CartSchema, CartItemCreate, CartItemUpdate
from app.core.auth import get_current_user

router = APIRouter(prefix="/cart", tags=["Cart"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=CartSchema)
def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Fetch the current user's cart."""
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        # Create an empty cart if it doesn't exist
        cart = Cart(user_id=current_user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart

@router.post("/items", response_model=CartSchema)
def add_to_cart(
    item_data: CartItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add an item to the cart or update quantity if it exists."""
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.add(cart)
        db.flush()

    # Get product to snapshot price
    product = db.query(Product).filter(Product.id == item_data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    existing_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == item_data.product_id
    ).first()

    if existing_item:
        existing_item.quantity += item_data.quantity
        if existing_item.quantity <= 0:
            db.delete(existing_item)
    else:
        new_item = CartItem(
            cart_id=cart.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            unit_price_snapshot=product.original_price # Or should we use tier pricing?
        )
        db.add(new_item)

    db.commit()
    db.refresh(cart)
    return cart

@router.put("/items/{product_id}", response_model=CartSchema)
def update_cart_item(
    product_id: UUID,
    update_data: CartItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update item quantity in cart."""
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == product_id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found in cart")

    if update_data.quantity <= 0:
        db.delete(item)
    else:
        item.quantity = update_data.quantity
    
    db.commit()
    db.refresh(cart)
    return cart

@router.delete("/items/{product_id}", response_model=CartSchema)
def remove_from_cart(
    product_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove an item from the cart."""
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == product_id
    ).first()

    if item:
        db.delete(item)
        db.commit()
    
    db.refresh(cart)
    return cart

@router.delete("/clear", response_model=CartSchema)
def clear_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear the cart."""
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if cart:
        db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
        db.commit()
        db.refresh(cart)
    return cart
