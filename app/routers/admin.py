from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from app.database import SessionLocal
from app.models.product import Product
from app.models.category import Category
from app.models.order import Order
from app.models.product_image import ProductImage
from app.models.inventory import Inventory
from app.models.tier_pricing import ProductTierPricing
from pydantic import BaseModel
from typing import List, Optional
import uuid

router = APIRouter(prefix="/admin", tags=["Admin Panel"])

BASE_STORAGE_URL = "https://vkkcnnbvfttvnzamvcsh.supabase.co/storage/v1/object/public/Product%20Images/"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ──── SCHEMAS ────
class TierPricingSchema(BaseModel):
    min_qty: int
    max_qty: Optional[int]
    unit_price: float

class ProductCreateSchema(BaseModel):
    name: str
    sku: str
    barcode: Optional[str] = None
    category_id: Optional[uuid.UUID] = None
    description: Optional[str] = None
    brand: Optional[str] = None
    base_unit: Optional[str] = None
    weight: Optional[str] = None
    is_halal: bool = True
    status: str = "active"
    badge: Optional[str] = None
    original_price: Optional[float] = None
    packaging: Optional[str] = None
    moq_text: Optional[str] = None
    is_popular: bool = False
    is_featured: bool = False
    images: List[str] = [] # List of image URLs
    stock: int = 0
    tier_pricing: List[TierPricingSchema] = []

class CategoryCreateSchema(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    malay_name: Optional[str] = None
    sort_order: int = 0
    icon: Optional[str] = None
    is_active: bool = True

# ──── PRODUCTS ────
@router.get("/products")
def admin_list_products(db: Session = Depends(get_db)):
    products = db.query(Product).options(
        joinedload(Product.category),
        joinedload(Product.inventory),
        joinedload(Product.images)
    ).all()
    
    res = []
    for p in products:
        img_path = p.images[0].image_url if p.images else None
        if img_path and not img_path.startswith(("http://", "https://")):
            img_path = BASE_STORAGE_URL + img_path

        res.append({
            "id": p.id,
            "name": p.name,
            "sku": p.sku,
            "category": p.category.name if p.category else None,
            "price": float(p.original_price) if p.original_price else 0,
            "stock": p.inventory.stock_quantity if p.inventory else 0,
            "image": img_path,
            "status": p.status
        })
    return res

@router.post("/products")
def create_product(data: ProductCreateSchema, db: Session = Depends(get_db)):
    # 1. Create Product
    product = Product(
        name=data.name,
        sku=data.sku,
        barcode=data.barcode,
        category_id=data.category_id,
        description=data.description,
        brand=data.brand,
        base_unit=data.base_unit,
        weight=data.weight,
        is_halal=data.is_halal,
        status=data.status,
        badge=data.badge,
        original_price=data.original_price,
        packaging=data.packaging,
        moq_text=data.moq_text,
        is_popular=data.is_popular,
        is_featured=data.is_featured
    )
    db.add(product)
    db.flush() # get product.id

    # 2. Add Stock
    inventory = Inventory(product_id=product.id, stock_quantity=data.stock)
    db.add(inventory)

    # 3. Add Images
    for i, img_url in enumerate(data.images):
        db.add(ProductImage(product_id=product.id, image_url=img_url, sort_order=i))

    # 4. Add Tier Pricing
    for tp in data.tier_pricing:
        db.add(ProductTierPricing(
            product_id=product.id,
            min_qty=tp.min_qty,
            max_qty=tp.max_qty,
            unit_price=tp.unit_price
        ))

    db.commit()
    return {"status": "success", "id": product.id}

@router.delete("/products/{pid}")
def delete_product(pid: uuid.UUID, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == pid).first()
    if not product:
        raise HTTPException(404, "Product not found")
    
    # Delete related data manually if not cascaded
    db.query(Inventory).filter(Inventory.product_id == pid).delete()
    db.query(ProductImage).filter(ProductImage.product_id == pid).delete()
    db.query(ProductTierPricing).filter(ProductTierPricing.product_id == pid).delete()
    
    db.delete(product)
    db.commit()
    return {"status": "success"}

# ──── CATEGORIES ────
@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()

@router.post("/categories")
def create_category(data: CategoryCreateSchema, db: Session = Depends(get_db)):
    cat = Category(**data.dict())
    db.add(cat)
    db.commit()
    return {"status": "success", "id": cat.id}

@router.delete("/categories/{cid}")
def delete_category(cid: uuid.UUID, db: Session = Depends(get_db)):
    cat = db.query(Category).filter(Category.id == cid).first()
    if not cat: raise HTTPException(404)
    db.delete(cat)
    db.commit()
    return {"status": "success"}

# ──── ORDERS ────
@router.get("/orders")
def list_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).options(joinedload(Order.user)).order_by(desc(Order.created_at)).all()
    res = []
    for o in orders:
        res.append({
            "id": o.id,
            "order_number": o.order_number,
            "customer": o.user.name if o.user else "Anonymous",
            "date": o.created_at.strftime("%Y-%m-%d %H:%M"),
            "total": float(o.total_amount) if o.total_amount else 0,
            "status": o.order_status
        })
    return res
