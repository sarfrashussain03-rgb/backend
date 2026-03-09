"""
Stripe Payment Router
Handles PaymentSheet creation and webhook events.
Uses Stripe TEST MODE only.
"""
import os
import stripe
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.database import SessionLocal
from app.models.order import Order
from app.models.user import User
from app.core.auth import get_current_user

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env'))

# Configure Stripe with test secret key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_XXXX")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "pk_test_XXXX")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_XXXX")

router = APIRouter(prefix="/payment", tags=["Payment"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ──── Request Schema ────
class PaymentSheetRequest(BaseModel):
    """Request body for creating a PaymentSheet session."""
    amount: float  # Total amount in RM (e.g. 25.50)
    currency: str = "myr"  # Malaysian Ringgit


# ──── POST /payment-sheet ────
@router.post("/payment-sheet")
def create_payment_sheet(
    request: PaymentSheetRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Creates Stripe Customer, EphemeralKey, and PaymentIntent.
    Returns the data needed by Flutter to initialize the PaymentSheet.
    
    Flow (as per Stripe docs):
    1. Create or reuse a Stripe Customer
    2. Create an EphemeralKey for the customer
    3. Create a PaymentIntent with the amount
    4. Return all secrets to the client
    """
    try:
        # Convert RM amount to sen (cents) — Stripe expects integer amounts
        amount_in_cents = int(round(request.amount * 100))

        if amount_in_cents < 200:  # Stripe minimum is 2.00 MYR (200 sen)
            raise HTTPException(
                status_code=400,
                detail="Minimum payment amount is RM 2.00"
            )

        # Step 1: Create a Stripe Customer
        # In production, you'd store the stripe_customer_id on the User model
        # and reuse it. For test mode, creating a new one each time is fine.
        customer = stripe.Customer.create(
            email=current_user.email,
            name=current_user.name,
            metadata={
                "app_user_id": str(current_user.id),
            }
        )

        # Step 2: Create an Ephemeral Key for the customer
        ephemeral_key = stripe.EphemeralKey.create(
            customer=customer.id,
            stripe_version="2023-10-16",
        )

        # Step 3: Create a PaymentIntent
        payment_intent = stripe.PaymentIntent.create(
            amount=amount_in_cents,
            currency=request.currency,
            customer=customer.id,
            automatic_payment_methods={"enabled": True},
            metadata={
                "app_user_id": str(current_user.id),
            }
        )

        # Step 4: Return all the data Flutter needs
        return {
            "paymentIntent": payment_intent.client_secret,
            "ephemeralKey": ephemeral_key.secret,
            "customer": customer.id,
            "publishableKey": STRIPE_PUBLISHABLE_KEY,
            "paymentIntentId": payment_intent.id,
        }

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment setup failed: {str(e)}")


# ──── POST /webhook ────
@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Stripe Webhook endpoint.
    Listens for payment_intent.succeeded / payment_intent.payment_failed events.
    
    For testing:
    - You can use Stripe CLI: `stripe listen --forward-to localhost:8000/api/payment/webhook`
    - Or temporarily trust client-side success (which we do in this test setup)
    
    In production, this should be the primary way to confirm payments.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        # Verify webhook signature (skip if no webhook secret configured)
        if STRIPE_WEBHOOK_SECRET and STRIPE_WEBHOOK_SECRET != "whsec_XXXX":
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
        else:
            # For testing without webhook secret — parse payload directly
            import json
            event = json.loads(payload)

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the event
    event_type = event.get("type", "")

    if event_type == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        payment_intent_id = payment_intent["id"]

        # Find order with this payment intent and mark as paid
        order = db.query(Order).filter(
            Order.stripe_payment_intent_id == payment_intent_id
        ).first()

        if order:
            order.payment_status = "paid"
            db.commit()
            print(f"✅ Payment succeeded for order {order.order_number}")
        else:
            print(f"⚠️ No order found for PaymentIntent {payment_intent_id}")

    elif event_type == "payment_intent.payment_failed":
        payment_intent = event["data"]["object"]
        payment_intent_id = payment_intent["id"]

        order = db.query(Order).filter(
            Order.stripe_payment_intent_id == payment_intent_id
        ).first()

        if order:
            order.payment_status = "failed"
            db.commit()
            print(f"❌ Payment failed for order {order.order_number}")

    elif event_type == "payment_intent.processing":
        print("⏳ Payment is processing...")

    return {"status": "ok"}
