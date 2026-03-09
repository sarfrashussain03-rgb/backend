"""
AI Agent tools for the wholesale chat assistant.
These tools give the LangGraph agent access to the product database,
cart operations, and business analytics.
"""

import json
import uuid
import logging
from typing import Optional, Annotated
from langchain_core.tools import tool, InjectedToolArg
from langchain_core.runnables.config import RunnableConfig
from sqlalchemy.orm import joinedload
from sqlalchemy import or_, and_
from app.database import SessionLocal
from app.models.user import User
from app.models.product import Product
from app.models.category import Category
from app.models.inventory import Inventory
from app.models.tier_pricing import ProductTierPricing
from app.models.cart import Cart, CartItem

BASE_STORAGE_URL = "https://vkkcnnbvfttvnzamvcsh.supabase.co/storage/v1/object/public/Product%20Images/"


def _get_db():
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise


def _serialize_product(p, db=None):
    """Convert a Product ORM object into a dict for the agent."""
    base_price = None
    if p.tier_pricing:
        base_price = float(min(t.unit_price for t in p.tier_pricing))

    imgs = sorted(p.images, key=lambda x: x.sort_order) if p.images else []
    primary_image = (BASE_STORAGE_URL + imgs[0].image_url) if imgs else None
    stock = p.inventory.stock_quantity if p.inventory else 0

    tier_pricing_list = []
    if p.tier_pricing:
        for t in sorted(p.tier_pricing, key=lambda x: x.min_qty):
            tier_pricing_list.append({
                "min_qty": t.min_qty,
                "max_qty": t.max_qty,
                "price": float(t.unit_price),
            })

    all_images = [(BASE_STORAGE_URL + img.image_url) for img in imgs] if imgs else []

    return {
        "id": str(p.id),
        "name": p.name,
        "sku": p.sku,
        "brand": p.brand,
        "description": p.description,
        "base_unit": p.base_unit,
        "weight": p.weight,
        "base_price": base_price,
        "original_price": float(p.original_price) if p.original_price else None,
        "stock": stock,
        "badge": p.badge,
        "is_halal": p.is_halal,
        "status": p.status,
        "packaging": p.packaging,
        "moq_text": p.moq_text,
        "category": {"id": str(p.category.id), "name": p.category.name} if p.category else None,
        "image": primary_image,
        "images": all_images,
        "tier_pricing": tier_pricing_list,
    }


@tool
def search_products(query: str, category: Optional[str] = None, brand: Optional[str] = None, min_qty: int = 1) -> str:
    """Search products by name, description, category, or brand.
    Use this to find products in the wholesale catalog.
    Returns a list of matching products with name, price, stock, and other details.

    Args:
        query: Search keyword (product name, description, or use-case like 'biryani rice', 'cooking oil')
        category: Optional category name to filter (e.g. 'Vegetables', 'Spices', 'Frozen Food')
        brand: Optional brand name to filter
        min_qty: Minimum quantity needed (default 1)
    """
    db = _get_db()
    try:
        q = (
            db.query(Product)
            .filter(Product.status == "active")
            .options(
                joinedload(Product.images),
                joinedload(Product.inventory),
                joinedload(Product.tier_pricing),
                joinedload(Product.category),
            )
        )

        if query:
            search_query = query.lower().strip()
            # Basic singularization for typical English words (tomatoes -> tomato, apples -> apple)
            if search_query.endswith("es") and len(search_query) > 3:
                search_query = search_query[:-2]
            elif search_query.endswith("s") and len(search_query) > 2:
                search_query = search_query[:-1]

            words = search_query.split()
            word_filters = []
            for word in words:
                search_term = f"%{word}%"
                word_filters.append(
                    or_(
                        Product.name.ilike(search_term),
                        Product.description.ilike(search_term),
                        Product.brand.ilike(search_term),
                        Product.sku.ilike(search_term)
                    )
                )
            if word_filters:
                # Use OR across words so that "fresh tomatoes 10kg" matches "Tomato"
                q = q.filter(or_(*word_filters))

        if category:
            q = q.join(Product.category).filter(Category.name.ilike(f"%{category}%"))

        if brand:
            q = q.filter(Product.brand.ilike(f"%{brand}%"))

        products = q.limit(20).all()
        results = [_serialize_product(p) for p in products]

        if not results:
            return json.dumps({"message": f"No products found for '{query}'", "products": []})

        return json.dumps({"message": f"Found {len(results)} products", "products": results})
    finally:
        db.close()


@tool
def get_product_details(product_id: str) -> str:
    """Get comprehensive details of a specific product including quality grades, bulk pricing tiers, stock availability, and packaging info.

    Args:
        product_id: The UUID of the product to get details for
    """
    db = _get_db()
    try:
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
            return json.dumps({"error": f"Product with ID {product_id} not found"})

        result = _serialize_product(product)
        return json.dumps(result)
    finally:
        db.close()


@tool
def add_to_cart(
    items: list[dict],
    config: Annotated[RunnableConfig, InjectedToolArg],
) -> dict:
    """Add one or more products to the user's shopping cart.
    ALWAYS call this tool when the user asks to add something to their cart.
    
    Args:
        items: A list of products to add. Each item MUST have:
               'product_id' (str): The UUID of the product.
               'quantity' (int): The number of units to add (default 1).
    """
    # Get user_id safely from the config metadata (injected by the server)
    configurable = config.get("configurable", {})
    raw_user_id = configurable.get("user_id", "anonymous")
    try:
        val_user_id = uuid.UUID(raw_user_id)
    except (ValueError, AttributeError):
        # Generate a deterministic UUID for non-UUID sessions (e.g. 'anonymous')
        val_user_id = uuid.uuid5(uuid.NAMESPACE_DNS, str(raw_user_id))

    logger = logging.getLogger(__name__)
    logger.info(f"--- TOOL CALL: add_to_cart ---")
    logger.info(f"Items: {items}")
    
    configurable = config.get("configurable", {})
    raw_user_id = configurable.get("user_id", "anonymous")
    logger.info(f"Raw user_id: {raw_user_id}")
    db = _get_db()
    try:
        # Check if user exists, create if not (for anonymous or test users)
        user = db.query(User).filter(User.id == val_user_id).first()
        if not user:
            logger.info(f"Creating dummy user record for {val_user_id}")
            user = User(id=val_user_id, firebase_uid=f"anon-{raw_user_id}", name="Test User")
            db.add(user)
            db.flush()

        # Find or create cart for user
        cart = db.query(Cart).filter(Cart.user_id == val_user_id).first()
        if not cart:
            cart = Cart(user_id=val_user_id)
            db.add(cart)
            db.flush()

        added_items = []
        for item in items:
            product_id = item.get("product_id")
            quantity = item.get("quantity", 1)

            # Get product to verify it exists and get pricing
            product = (
                db.query(Product)
                .filter(Product.id == product_id)
                .options(
                    joinedload(Product.tier_pricing),
                    joinedload(Product.images),
                    joinedload(Product.inventory),
                    joinedload(Product.category),
                )
                .first()
            )

            if not product:
                added_items.append({"product_id": product_id, "status": "error", "message": "Product not found"})
                continue

            # Find best price based on quantity
            unit_price = None
            if product.tier_pricing:
                for tier in sorted(product.tier_pricing, key=lambda t: t.min_qty, reverse=True):
                    if quantity >= tier.min_qty:
                        unit_price = tier.unit_price
                        break
                if unit_price is None:
                    unit_price = min(t.unit_price for t in product.tier_pricing)

            # Check if item already in cart
            existing = (
                db.query(CartItem)
                .filter(CartItem.cart_id == cart.id, CartItem.product_id == product_id)
                .first()
            )

            if existing:
                existing.quantity += quantity
                existing.unit_price_snapshot = unit_price
            else:
                cart_item = CartItem(
                    cart_id=cart.id,
                    product_id=product_id,
                    quantity=quantity,
                    unit_price_snapshot=unit_price,
                )
                db.add(cart_item)

            added_items.append({
                "product_id": product_id,
                "product_name": product.name,
                "quantity": quantity,
                "unit_price": float(unit_price) if unit_price else None,
                "status": "added",
                "product_details": _serialize_product(product),
            })

        db.commit()

        total = sum(
            i["unit_price"] * i["quantity"]
            for i in added_items
            if i.get("status") == "added" and i.get("unit_price")
        )

        return {
            "message": f"Successfully added {len([i for i in added_items if i['status'] == 'added'])} items to cart",
            "items": added_items,
            "cart_total": total,
            "cart_updated": True,
        }
    except Exception as e:
        db.rollback()
        return {"error": str(e), "cart_updated": False}
    finally:
        db.close()


@tool
def get_all_categories() -> str:
    """Get all available product categories in the wholesale catalog.
    Use this to understand what product categories are available before searching.
    """
    db = _get_db()
    try:
        categories = db.query(Category).filter(Category.is_active == True).all()
        results = []
        for c in categories:
            results.append({
                "id": str(c.id),
                "name": c.name,
                "description": c.description,
                "product_count": c.product_count,
            })
        return json.dumps({"categories": results})
    finally:
        db.close()


@tool
def check_stock_availability(product_ids: list[str]) -> str:
    """Check stock availability for multiple products at once.

    Args:
        product_ids: List of product UUIDs to check stock for
    """
    db = _get_db()
    try:
        results = []
        for pid in product_ids:
            inv = db.query(Inventory).filter(Inventory.product_id == pid).first()
            product = db.query(Product).filter(Product.id == pid).first()
            if product:
                results.append({
                    "product_id": str(pid),
                    "product_name": product.name,
                    "stock_quantity": inv.stock_quantity if inv else 0,
                    "restock_date": str(inv.restock_date) if inv and inv.restock_date else None,
                    "in_stock": (inv.stock_quantity > 0) if inv else False,
                })
        return json.dumps({"stock_info": results})
    finally:
        db.close()


@tool
def estimate_business_metrics(
    setup_type: str,
    daily_servings: int,
    budget: float,
    ingredient_costs: Optional[list[dict]] = None,
) -> str:
    """Estimate business metrics for a food business setup.
    Calculates cost per serving, profit margins, monthly costs, and reorder estimates.

    Args:
        setup_type: Type of business (e.g. 'biryani restaurant', 'juice shop', 'catering')
        daily_servings: Expected number of servings per day
        budget: Total initial budget in RM
        ingredient_costs: Optional list of ingredient costs [{"name": "rice", "cost_per_unit": 5.0, "units_per_serving": 0.5}]
    """
    if ingredient_costs is None:
        ingredient_costs = []

    # Calculate per-serving cost from provided ingredients
    cost_per_serving = sum(
        item.get("cost_per_unit", 0) * item.get("units_per_serving", 0)
        for item in ingredient_costs
    )

    # Estimate if no ingredients provided
    if cost_per_serving == 0:
        # Rough estimates based on setup type
        estimates = {
            "biryani restaurant": 8.0,
            "nasi lemak": 3.0,
            "juice shop": 4.0,
            "catering": 12.0,
            "default": 6.0,
        }
        cost_per_serving = estimates.get(setup_type.lower(), estimates["default"])

    monthly_servings = daily_servings * 30
    monthly_ingredient_cost = cost_per_serving * monthly_servings

    # Suggest selling prices (2x-3x markup)
    suggested_price_min = cost_per_serving * 2
    suggested_price_max = cost_per_serving * 3

    months_of_operation = budget / monthly_ingredient_cost if monthly_ingredient_cost > 0 else 0

    return json.dumps({
        "setup_type": setup_type,
        "daily_servings": daily_servings,
        "budget": budget,
        "cost_per_serving": round(cost_per_serving, 2),
        "monthly_ingredient_cost": round(monthly_ingredient_cost, 2),
        "suggested_selling_price": {
            "min": round(suggested_price_min, 2),
            "max": round(suggested_price_max, 2),
        },
        "estimated_monthly_revenue": {
            "conservative": round(suggested_price_min * monthly_servings, 2),
            "optimistic": round(suggested_price_max * monthly_servings, 2),
        },
        "estimated_monthly_profit": {
            "conservative": round((suggested_price_min - cost_per_serving) * monthly_servings, 2),
            "optimistic": round((suggested_price_max - cost_per_serving) * monthly_servings, 2),
        },
        "months_budget_lasts": round(months_of_operation, 1),
        "reorder_frequency": "Every 1-2 weeks for perishables, monthly for dry goods",
    })


@tool
def calculate_ingredient_quantities(
    product_type: str,
    servings_per_day: int,
    days: int = 30,
) -> str:
    """Calculate the monthly ingredient quantities needed for a food/beverage business.
    Use this BEFORE searching for products to know what quantities to order.
    
    Returns a list of ingredients with:
    - name: ingredient name
    - quantity_per_serving: amount needed per serving (with unit)
    - total_quantity: total amount needed for the period
    - search_keyword: what to search for in the product catalog
    
    Args:
        product_type: The product being sold (e.g. "tea", "coffee", "nasi lemak", "biryani", "juice", "roti canai")
        servings_per_day: Number of servings/cups/plates sold per day
        days: Number of days to calculate for (default 30 = 1 month)
    """
    total_servings = servings_per_day * days
    
    # Ingredient recipes per serving
    recipes = {
        "tea": [
            {"name": "Black Tea Leaves", "qty_per_serving_g": 2.5, "unit": "g", "search_keyword": "tea leaves"},
            {"name": "Sugar", "qty_per_serving_g": 8, "unit": "g", "search_keyword": "sugar"},
            {"name": "Creamer / Milk Powder", "qty_per_serving_g": 5, "unit": "g", "search_keyword": "creamer"},
            {"name": "Sweetened Condensed Milk (optional)", "qty_per_serving_g": 10, "unit": "g", "search_keyword": "condensed milk"},
        ],
        "teh tarik": [
            {"name": "Black Tea Leaves", "qty_per_serving_g": 3, "unit": "g", "search_keyword": "tea leaves"},
            {"name": "Sugar", "qty_per_serving_g": 10, "unit": "g", "search_keyword": "sugar"},
            {"name": "Sweetened Condensed Milk", "qty_per_serving_g": 20, "unit": "g", "search_keyword": "condensed milk"},
            {"name": "Evaporated Milk", "qty_per_serving_ml": 20, "unit": "ml", "search_keyword": "evaporated milk"},
        ],
        "coffee": [
            {"name": "Coffee Powder", "qty_per_serving_g": 10, "unit": "g", "search_keyword": "coffee powder"},
            {"name": "Sugar", "qty_per_serving_g": 8, "unit": "g", "search_keyword": "sugar"},
            {"name": "Non-Dairy Creamer", "qty_per_serving_g": 5, "unit": "g", "search_keyword": "creamer"},
            {"name": "Sweetened Condensed Milk", "qty_per_serving_g": 15, "unit": "g", "search_keyword": "condensed milk"},
        ],
        "nasi lemak": [
            {"name": "Rice", "qty_per_serving_g": 150, "unit": "g", "search_keyword": "rice"},
            {"name": "Coconut Milk", "qty_per_serving_ml": 50, "unit": "ml", "search_keyword": "coconut milk"},
            {"name": "Sambal Paste", "qty_per_serving_g": 30, "unit": "g", "search_keyword": "sambal"},
            {"name": "Dried Anchovies (Ikan Bilis)", "qty_per_serving_g": 20, "unit": "g", "search_keyword": "ikan bilis"},
            {"name": "Roasted Peanuts", "qty_per_serving_g": 15, "unit": "g", "search_keyword": "peanuts"},
            {"name": "Eggs", "qty_per_serving_units": 1, "unit": "pcs", "search_keyword": "eggs"},
        ],
        "biryani": [
            {"name": "Basmati Rice", "qty_per_serving_g": 200, "unit": "g", "search_keyword": "basmati rice"},
            {"name": "Chicken", "qty_per_serving_g": 200, "unit": "g", "search_keyword": "chicken"},
            {"name": "Biryani Spice Mix", "qty_per_serving_g": 15, "unit": "g", "search_keyword": "biryani spice"},
            {"name": "Cooking Oil", "qty_per_serving_ml": 20, "unit": "ml", "search_keyword": "cooking oil"},
            {"name": "Onions", "qty_per_serving_g": 50, "unit": "g", "search_keyword": "onion"},
            {"name": "Yogurt", "qty_per_serving_g": 30, "unit": "g", "search_keyword": "yogurt"},
        ],
        "roti canai": [
            {"name": "All-Purpose Flour", "qty_per_serving_g": 100, "unit": "g", "search_keyword": "flour"},
            {"name": "Ghee / Margarine", "qty_per_serving_g": 15, "unit": "g", "search_keyword": "ghee"},
            {"name": "Eggs", "qty_per_serving_units": 0.25, "unit": "pcs", "search_keyword": "eggs"},
            {"name": "Salt", "qty_per_serving_g": 2, "unit": "g", "search_keyword": "salt"},
            {"name": "Condensed Milk", "qty_per_serving_g": 10, "unit": "g", "search_keyword": "condensed milk"},
        ],
        "juice": [
            {"name": "Fresh Fruits (mixed)", "qty_per_serving_g": 200, "unit": "g", "search_keyword": "fruit"},
            {"name": "Sugar / Simple Syrup", "qty_per_serving_g": 15, "unit": "g", "search_keyword": "sugar"},
            {"name": "Ice", "qty_per_serving_g": 100, "unit": "g", "search_keyword": "ice"},
        ],
    }
    
    # Match product type (case-insensitive, partial match)
    matched_key = None
    product_lower = product_type.lower().strip()
    for key in recipes:
        if key in product_lower or product_lower in key:
            matched_key = key
            break
    
    # Default fallback for unknown types
    if not matched_key:
        return json.dumps({
            "product_type": product_type,
            "servings_per_day": servings_per_day,
            "days": days,
            "total_servings": total_servings,
            "note": f"No predefined recipe for '{product_type}'. Please list the ingredients manually.",
            "ingredients": []
        })
    
    ingredients = []
    for ing in recipes[matched_key]:
        qty_key = [k for k in ing if k.startswith("qty_per_serving")][0]
        qty_per = ing[qty_key]
        unit = ing["unit"]
        total = qty_per * total_servings
        
        # Convert to practical wholesale units
        if unit == "g" and total >= 1000:
            display_total = f"{total/1000:.2f} kg"
            order_qty_kg = round(total / 1000, 2)
        elif unit == "ml" and total >= 1000:
            display_total = f"{total/1000:.2f} L"
            order_qty_kg = round(total / 1000, 2)
        else:
            display_total = f"{total:.0f} {unit}"
            order_qty_kg = total
        
        ingredients.append({
            "name": ing["name"],
            "qty_per_serving": f"{qty_per} {unit}",
            "total_quantity": display_total,
            "order_quantity_value": order_qty_kg,
            "order_unit": "kg" if unit in ("g", "ml") and total >= 1000 else unit,
            "search_keyword": ing["search_keyword"],
        })
    
    return json.dumps({
        "product_type": matched_key,
        "servings_per_day": servings_per_day,
        "days": days,
        "total_servings": total_servings,
        "calculation_note": f"{servings_per_day} servings/day × {days} days = {total_servings} total servings",
        "ingredients": ingredients,
    })


# Collect all tools for the agent
all_tools = [
    search_products,
    get_product_details,
    add_to_cart,
    get_all_categories,
    check_stock_availability,
    estimate_business_metrics,
    calculate_ingredient_quantities,
]

