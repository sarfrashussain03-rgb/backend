import os
from dotenv import load_dotenv

# Load environment variables at the absolute start
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import product, home, category, chat, admin, order, cart, user, payment

app = FastAPI(title="Wholesale API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for images
# Assuming images are in a folder named 'static' or 'uploads'
# Given the user's data, we might need a folder 'assets' or just 'static'
# Let's create a 'static' folder if it doesn't exist
static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if not os.path.exists(static_path):
    os.makedirs(static_path)

app.mount("/static", StaticFiles(directory=static_path), name="static")

app.include_router(product.router, prefix="/api")
app.include_router(home.router, prefix="/api")
app.include_router(category.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(order.router, prefix="/api")
app.include_router(cart.router, prefix="/api")
app.include_router(user.router, prefix="/api")
app.include_router(payment.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Wholesale API Running"}