from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.database import SessionLocal
from app.models.category import Category
from app.models.product import Product

router = APIRouter(prefix="/categories", tags=["Categories"])

BASE_STORAGE_URL = "https://vkkcnnbvfttvnzamvcsh.supabase.co/storage/v1/object/public/Product%20Images/"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ──── Get All Categories ────
@router.get("/")
def get_categories(db: Session = Depends(get_db)):
    categories = (
        db.query(Category)
        .filter(Category.is_active == True)
        .order_by(Category.sort_order)
        .all()
    )

    return [
        {
            "id": str(c.id),
            "name": c.name,
            "description": c.description,
            "malay_name": c.malay_name,
            "icon": c.icon,
            "image": (BASE_STORAGE_URL + c.image_url) if c.image_url else None,
            "product_count": c.product_count,
        }
        for c in categories
    ]


# ──── Get Products by Category (Pagination + Sorting + Filtering + Search) ────
@router.get("/{category_id}/products")
def get_products_by_category(
    category_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=50),
    sort: str = Query("latest"),         # latest, name, price_low, price_high
    search: str = Query(None),           # search within category
    brand: str = Query(None),            # filter by brand
    status: str = Query(None),           # active, inactive
    badge: str = Query(None),            # BESTSELLER, HOT, NEW, PROMO
    in_stock: bool = Query(None),        # true = only in stock items
    db: Session = Depends(get_db),
):
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    query = (
        db.query(Product)
        .filter(Product.category_id == category_id)
        .options(
            joinedload(Product.images),
            joinedload(Product.inventory),
            joinedload(Product.tier_pricing),
        )
    )

    # ── Filters ──
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Product.name.ilike(search_term))
            | (Product.sku.ilike(search_term))
            | (Product.description.ilike(search_term))
            | (Product.brand.ilike(search_term))
            | (Product.barcode.ilike(search_term))
        )

    if brand:
        query = query.filter(Product.brand.ilike(f"%{brand}%"))

    if status:
        query = query.filter(Product.status == status)
    else:
        # Default: only active products
        query = query.filter(Product.status == "active")

    if badge:
        query = query.filter(Product.badge == badge)

    if in_stock is True:
        query = query.join(Product.inventory).filter(
            Product.inventory.has(stock_quantity__gt=0)
        )

    # ── Sorting ──
    if sort == "latest":
        query = query.order_by(Product.id.desc())
    elif sort == "name":
        query = query.order_by(Product.name.asc())
    elif sort == "price_low":
        query = query.order_by(Product.id.asc())  # Will sort client-side by base_price
    elif sort == "price_high":
        query = query.order_by(Product.id.desc())

    total = query.count()
    products = query.offset((page - 1) * limit).limit(limit).all()

    # Serialize products
    serialized = []
    for p in products:
        base_price = None
        if p.tier_pricing:
            base_price = float(min(t.unit_price for t in p.tier_pricing))

        images = sorted(p.images, key=lambda x: x.sort_order) if p.images else []
        primary_image = (BASE_STORAGE_URL + images[0].image_url) if images else None
        stock = p.inventory.stock_quantity if p.inventory else 0
        restock_date = str(p.inventory.restock_date) if p.inventory and p.inventory.restock_date else None

        serialized.append({
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
        })

    # Sort by price on the server if requested
    if sort == "price_low":
        serialized.sort(key=lambda x: x["base_price"] or 0)
    elif sort == "price_high":
        serialized.sort(key=lambda x: x["base_price"] or 0, reverse=True)

    return {
        "category": {
            "id": str(category.id),
            "name": category.name,
            "description": category.description,
            "malay_name": category.malay_name,
            "icon": category.icon,
            "image": (BASE_STORAGE_URL + category.image_url) if category.image_url else None,
        },
        "page": page,
        "limit": limit,
        "total": total,
        "sort": sort,
        "products": serialized,
    }