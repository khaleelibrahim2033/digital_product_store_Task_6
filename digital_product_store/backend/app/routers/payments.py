import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..config import settings
from ..database import get_db
from ..models import User, Cart, Order, OrderItem, Payment
from ..auth import get_current_user

router = APIRouter(prefix="/payments", tags=["Payments"])
stripe.api_key = settings.STRIPE_SECRET_KEY

@router.post("/create-checkout-session")
def create_checkout_session(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart = db.query(Cart).filter(Cart.user_id == user.id).first()
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    total = sum(i.product.price*i.quantity for i in cart.items)
    order = Order(user_id=user.id, status="PENDING", total_amount=round(total, 2))
    db.add(order); db.flush()
    for item in cart.items:
        order.items.append(OrderItem(product_id=item.product_id, product_name=item.product.name,
                                     unit_price=item.product.price, quantity=item.quantity))
    order.payment = Payment(status="PENDING", amount=round(total, 2))
    db.flush()
    if not settings.STRIPE_SECRET_KEY:
        # Local development fallback: keep the order PENDING and expose a safe demo URL.
        order.stripe_session_id = f"demo_{order.id}"
        db.commit()
        return {"order_id": order.id, "checkout_url": f"{settings.FRONTEND_URL}/orders?demo_payment={order.id}"}
    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=[{"price_data": {"currency": "usd", "product_data": {"name": i.product.name},
                         "unit_amount": int(round(i.product.price*100))},
                        "quantity": i.quantity} for i in cart.items],
            success_url=f"{settings.FRONTEND_URL}/orders?payment=success&session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.FRONTEND_URL}/cart?payment=cancelled",
            metadata={"order_id": str(order.id), "user_id": str(user.id)}
        )
        order.stripe_session_id = session.id
        db.commit()
        return {"order_id": order.id, "checkout_url": session.url}
    except stripe.error.StripeError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Stripe error: {str(exc)}")

@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig = request.headers.get("stripe-signature")
    try:
        if settings.STRIPE_WEBHOOK_SECRET:
            event = stripe.Webhook.construct_event(payload, sig, settings.STRIPE_WEBHOOK_SECRET)
        else:
            event = stripe.Event.construct_from(__import__("json").loads(payload), stripe.api_key)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid webhook signature or payload")
    event_type = event["type"]
    obj = event["data"]["object"]
    session_id = obj.get("id") or obj.get("checkout_session")
    order = db.query(Order).filter(Order.stripe_session_id == session_id).first()
    if order:
        if event_type == "checkout.session.completed":
            order.status = "PAID"
            if order.payment:
                order.payment.status = "PAID"
                order.payment.stripe_payment_intent_id = obj.get("payment_intent")
            cart = db.query(Cart).filter(Cart.user_id == order.user_id).first()
            if cart:
                cart.items.clear()
        elif event_type in ("checkout.session.expired", "payment_intent.payment_failed"):
            order.status = "FAILED" if "failed" in event_type else "CANCELLED"
            if order.payment:
                order.payment.status = order.status
        db.commit()
    return {"received": True}
