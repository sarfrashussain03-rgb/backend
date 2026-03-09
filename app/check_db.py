import os
import sys

# Add backend dir to path if not already
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.product import Product

db = SessionLocal()
try:
    products = db.query(Product).limit(50).all()
    print("Products in DB:")
    for p in products:
        print(f" - {p.name} (SKU: {p.sku})")
finally:
    db.close()
