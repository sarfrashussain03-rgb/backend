from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from app.database import SessionLocal
from app.models.category import Category
from app.models.product import Product
from app.models.banner import Banner

router = APIRouter(tags=["Home"])

BASE_STORAGE_URL = "https://vkkcnnbvfttvnzamvcsh.supabase.co/storage/v1/object/public/Product%20Images/"
BASE_CATEGORY_STORAGE_URL = "https://vkkcnnbvfttvnzamvcsh.supabase.co/storage/v1/object/public/Product%20Images/"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _serialize_product_card(p):
    """Serialize a product for card display (listing / popular / similar)."""
    # Get base price from first tier
    base_price = None
    if p.tier_pricing:
        base_price = float(min(t.unit_price for t in p.tier_pricing))

    # Get primary image
    images = sorted(p.images, key=lambda x: x.sort_order) if p.images else []
    primary_image = (BASE_STORAGE_URL + images[0].image_url) if images else None

    # Stock info
    stock = p.inventory.stock_quantity if p.inventory else 0
    restock_date = str(p.inventory.restock_date) if p.inventory and p.inventory.restock_date else None

    return {
        "id": str(p.id),
        "name": p.name,
        "sku": p.sku,
        "barcode": p.barcode,
        "brand": p.brand,
        "base_unit": p.base_unit,
        "weight": p.weight,
        "badge": p.badge,
        "base_price": base_price,
        "original_price": float(p.original_price) if p.original_price else None,
        "moq_text": p.moq_text,
        "is_halal": p.is_halal,
        "status": p.status,
        "stock": stock,
        "restock_date": restock_date,
        "image": primary_image,
        "images": [BASE_STORAGE_URL + img.image_url for img in images],
    }


@router.get("/home")
def get_home(db: Session = Depends(get_db)):
    # Categories (top 6, ordered by sort_order)
    categories = (
        db.query(Category)
        .filter(Category.is_active == True)
        .order_by(Category.sort_order)
        .limit(6)
        .all()
    )

    # Most Popular products (with eager loading)
    popular_products = (
        db.query(Product)
        .filter(Product.is_popular == True, Product.status == "active")
        .options(
            joinedload(Product.images),
            joinedload(Product.inventory),
            joinedload(Product.tier_pricing),
        )
        .limit(10)
        .all()
    )

    # Banners
    banners = (
        db.query(Banner)
        .filter(Banner.is_active == True)
        .order_by(Banner.sort_order)
        .all()
    )

    # Featured / New Arrivals
    new_products = (
        db.query(Product)
        .filter(Product.is_featured == True, Product.status == "active")
        .options(
            joinedload(Product.images),
            joinedload(Product.inventory),
            joinedload(Product.tier_pricing),
        )
        .limit(6)
        .all()
    )

    return {
        "banners": [
            {
                "id": str(b.id),
                "title": b.title,
                "subtitle": b.subtitle,
                "image_url": (BASE_STORAGE_URL + b.image_url) if b.image_url else None,
                "badge_text": b.badge_text,
                "badge_color": b.badge_color,
                "button_text": b.button_text,
                "link_type": b.link_type,
                "link_value": b.link_value,
            }
            for b in banners
        ],
        "categories": [
            {
                "id": str(c.id),
                "name": c.name,
                "description": c.description,
                "malay_name": c.malay_name,
                "icon": c.icon,
                "image": (BASE_CATEGORY_STORAGE_URL + c.image_url) if c.image_url else None,
                "product_count": c.product_count,
            }
            for c in categories
        ],
        "most_popular": [_serialize_product_card(p) for p in popular_products],
        "new_arrivals": [_serialize_product_card(p) for p in new_products],
    }