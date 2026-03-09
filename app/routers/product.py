from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from app.database import SessionLocal
from app.models.product import Product
from app.models.category import Category

router = APIRouter(tags=["Products"])

BASE_STORAGE_URL = "https://vkkcnnbvfttvnzamvcsh.supabase.co/storage/v1/object/public/Product%20Images/"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ──── Product Detail ────
@router.get("/products/{product_id}")
def get_product(product_id: str, db: Session = Depends(get_db)):
    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .options(
            joinedload(Product.images),
            joinedload(Product.inventory),
            joinedload(Product.tier_pricing),
            joinedload(Product.category),
        )
        .first()
    )

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    images = sorted(product.images, key=lambda x: x.sort_order) if product.images else []
    stock = product.inventory.stock_quantity if product.inventory else 0
    restock_date = str(product.inventory.restock_date) if product.inventory and product.inventory.restock_date else None

    # ── Similar Items (same category, different product) ──
    similar_products = (
        db.query(Product)
        .filter(
            Product.category_id == product.category_id,
            Product.id != product.id,
            Product.status == "active",
        )
        .options(
            joinedload(Product.images),
            joinedload(Product.inventory),
            joinedload(Product.tier_pricing),
        )
        .limit(6)
        .all()
    )

    # ── Bought Together (products from other categories that are popular) ──
    bought_together = (
        db.query(Product)
        .filter(
            Product.category_id != product.category_id,
            Product.status == "active",
            Product.is_popular == True,
        )
        .options(
            joinedload(Product.images),
            joinedload(Product.inventory),
            joinedload(Product.tier_pricing),
        )
        .limit(6)
        .all()
    )

    def _card(p):
        bp = None
        if p.tier_pricing:
            bp = float(min(t.unit_price for t in p.tier_pricing))
        imgs = sorted(p.images, key=lambda x: x.sort_order) if p.images else []
        primary = imgs[0].image_url if imgs else None
        if primary and not primary.startswith(("http://", "https://")):
            primary = BASE_STORAGE_URL + primary
        st = p.inventory.stock_quantity if p.inventory else 0
        return {
            "id": str(p.id),
            "name": p.name,
            "sku": p.sku,
            "brand": p.brand,
            "base_price": bp,
            "original_price": float(p.original_price) if p.original_price else None,
            "image": primary,
            "stock": st,
            "badge": p.badge,
            "base_unit": p.base_unit,
            "weight": p.weight,
        }

    return {
        "id": str(product.id),
        "name": product.name,
        "sku": product.sku,
        "barcode": product.barcode,
        "brand": product.brand,
        "description": product.description,
        "base_unit": product.base_unit,
        "weight": product.weight,
        "packaging": product.packaging,
        "moq_text": product.moq_text,
        "is_halal": product.is_halal,
        "badge": product.badge,
        "status": product.status,
        "stock": stock,
        "restock_date": restock_date,
        "original_price": float(product.original_price) if product.original_price else None,
        "category": {
            "id": str(product.category.id) if product.category else None,
            "name": product.category.name if product.category else None,
        },
        "images": [
            (img.image_url if img.image_url.startswith(("http://", "https://")) else (BASE_STORAGE_URL + img.image_url))
            for img in images
        ],
        "tier_pricing": [
            {
                "min_qty": t.min_qty,
                "max_qty": t.max_qty,
                "price": float(t.unit_price),
            }
            for t in sorted(product.tier_pricing, key=lambda x: x.min_qty)
        ],
        "similar_items": [_card(p) for p in similar_products],
        "bought_together": [_card(p) for p in bought_together],
    }


# ──── Global search across all products ────
@router.get("/products")
def search_products(
    q: str = Query(None, description="Search query"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=50),
    sort: str = Query("latest"),
    brand: str = Query(None),
    category_id: str = Query(None),
    badge: str = Query(None),
    db: Session = Depends(get_db),
):
    query = (
        db.query(Product)
        .filter(Product.status == "active")
        .options(
            joinedload(Product.images),
            joinedload(Product.inventory),
            joinedload(Product.tier_pricing),
            joinedload(Product.category),
        )
    )

    if q:
        search_term = f"%{q}%"
        query = query.filter(
            (Product.name.ilike(search_term))
            | (Product.sku.ilike(search_term))
            | (Product.description.ilike(search_term))
            | (Product.brand.ilike(search_term))
            | (Product.barcode.ilike(search_term))
        )

    if brand:
        query = query.filter(Product.brand.ilike(f"%{brand}%"))

    if category_id:
        query = query.filter(Product.category_id == category_id)

    if badge:
        query = query.filter(Product.badge == badge)

    # Sorting
    if sort == "latest":
        query = query.order_by(Product.id.desc())
    elif sort == "name":
        query = query.order_by(Product.name.asc())

    total = query.count()
    products = query.offset((page - 1) * limit).limit(limit).all()

    serialized = []
    for p in products:
        base_price = None
        if p.tier_pricing:
            base_price = float(min(t.unit_price for t in p.tier_pricing))

        imgs = sorted(p.images, key=lambda x: x.sort_order) if p.images else []
        primary_image = imgs[0].image_url if imgs else None
        if primary_image and not primary_image.startswith(("http://", "https://")):
            primary_image = BASE_STORAGE_URL + primary_image
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
            "images": [
                (imgs[i].image_url if imgs[i].image_url.startswith(("http://", "https://")) else (BASE_STORAGE_URL + imgs[i].image_url))
                for i in range(len(imgs))
            ],
            "category": {
                "id": str(p.category.id) if p.category else None,
                "name": p.category.name if p.category else None,
            } if p.category else None,
        })

    # Sort by price on server
    if sort == "price_low":
        serialized.sort(key=lambda x: x["base_price"] or 0)
    elif sort == "price_high":
        serialized.sort(key=lambda x: x["base_price"] or 0, reverse=True)

    return {
        "query": q,
        "page": page,
        "limit": limit,
        "total": total,
        "sort": sort,
        "products": serialized,
    }