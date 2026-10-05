from math import ceil
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Order, OrderItem, Payment
from ..auth import get_current_user
from ..schemas import OrderOut, OrderList

router = APIRouter(prefix="/orders", tags=["Orders"])

def serialize_order(o):
    return {"id": o.id, "status": o.status, "total_amount": o.total_amount,
            "payment_status": o.payment.status if o.payment else "PENDING",
            "created_at": o.created_at.isoformat(),
            "items": [{"product_id": x.product_id, "product_name": x.product_name,
                       "unit_price": x.unit_price, "quantity": x.quantity,
                       "subtotal": round(x.unit_price*x.quantity, 2)} for x in o.items]}

@router.get("", response_model=OrderList)
def list_orders(page: int = Query(1, ge=1), limit: int = Query(5, ge=1, le=100),
                user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    q = db.query(Order).filter(Order.user_id == user.id).order_by(Order.id.desc())
    total = q.count()
    items = q.offset((page-1)*limit).limit(limit).all()
    return {"items": [serialize_order(o) for o in items], "page": page, "limit": limit,
            "total": total, "total_pages": ceil(total/limit) if total else 0}

@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    o = db.get(Order, order_id)
    if not o or o.user_id != user.id:
        raise HTTPException(status_code=404, detail="Order not found")
    return serialize_order(o)
