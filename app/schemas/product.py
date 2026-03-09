from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID


class TierPricingSchema(BaseModel):
    min_qty: int
    max_qty: Optional[int]
    price: float

    class Config:
        from_attributes = True


class ProductImageSchema(BaseModel):
    image_url: str
    sort_order: int = 0

    class Config:
        from_attributes = True


class ProductCardSchema(BaseModel):
    id: UUID
    name: str
    sku: Optional[str]
    barcode: Optional[str]
    brand: Optional[str]
    base_unit: Optional[str]
    weight: Optional[str]
    badge: Optional[str]
    base_price: Optional[float]
    original_price: Optional[float]
    moq_text: Optional[str]
    is_halal: Optional[bool]
    status: str
    stock: int
    restock_date: Optional[str]
    image: Optional[str]
    images: List[str]

    class Config:
        from_attributes = True


class CategorySchema(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    malay_name: Optional[str]
    icon: Optional[str]
    image: Optional[str]
    product_count: int = 0

    class Config:
        from_attributes = True


class ProductResponse(BaseModel):
    id: UUID
    name: str
    sku: Optional[str]
    barcode: Optional[str]
    brand: Optional[str]
    description: Optional[str]
    base_unit: Optional[str]
    weight: Optional[str]
    packaging: Optional[str]
    moq_text: Optional[str]
    is_halal: Optional[bool]
    badge: Optional[str]
    status: str
    stock: int
    restock_date: Optional[str]
    original_price: Optional[float]
    category: Optional[dict]
    images: List[str]
    tier_pricing: List[TierPricingSchema]
    similar_items: List[dict]
    bought_together: List[dict]

    class Config:
        from_attributes = True


class BannerSchema(BaseModel):
    id: UUID
    title: str
    subtitle: Optional[str]
    image_url: Optional[str]
    badge_text: Optional[str]
    badge_color: Optional[str]
    button_text: Optional[str]
    link_type: Optional[str]
    link_value: Optional[str]

    class Config:
        from_attributes = True