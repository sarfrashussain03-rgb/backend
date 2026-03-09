# Wholesale API Documentation

**Base URL:** `http://127.0.0.1:8000/api`

---

## 1. Home
### `GET /home`
Returns data for the application home screen, including top categories and featured products.

**Sample Response:**
```json
{
  "categories": [
    { "id": "uuid", "name": "Textiles", "image": "url" }
  ],
  "most_popular": [
    { "id": "uuid", "name": "Cotton Saree" }
  ]
}
```

---

## 2. Categories
### `GET /categories/`
Get a list of all active categories.

**Sample Response:**
```json
[
  {
    "id": "uuid",
    "name": "Electronics",
    "description": "Gadgets and more",
    "image": "url"
  }
]
```

### `GET /categories/{category_id}/products`
Get products belonging to a specific category.

**Query Parameters:**
- `page` (int): Default 1
- `limit` (int): Default 10 (max 50)
- `sort` (string): `latest` or `name`

**Sample Response:**
```json
{
  "category": "Electronics",
  "page": 1,
  "total": 25,
  "products": [
    { "id": "uuid", "name": "Laptop", "sku": "LP123", "status": "active" }
  ]
}
```

---

## 3. Products
### `GET /products/{product_id}`
Get comprehensive details of a specific product.

**Sample Response:**
```json
{
  "id": "uuid",
  "name": "Product Name",
  "description": "Full description",
  "images": ["url1", "url2"],
  "stock": 500,
  "tier_pricing": [
    { "min_qty": 10, "max_qty": 50, "price": 450.0 },
    { "min_qty": 51, "max_qty": null, "price": 400.0 }
  ]
}
```

---

## Swagger / Interactive Docs
The API provides built-in interactive documentation:
- **Swagger UI:** `http://127.0.0.1:8000/docs`
- **ReDoc:** `http://127.0.0.1:8000/redoc`
