from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..models import User, Product, Order, OrderItem
from ..auth import require_admin
from ..schemas import StatsOut, OrderList
from .orders import serialize_order

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/stats", response_model=StatsOut)
def stats(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    total_products = db.query(Product).filter(Product.is_active == True).count()
    total_orders = db.query(Order).count()
    paid_orders = db.query(Order).filter(Order.status == "PAID").count()
    revenue = db.query(func.coalesce(func.sum(Order.total_amount), 0)).filter(Order.status == "PAID").scalar()
    return {"total_products": total_products, "total_orders": total_orders,
            "paid_orders": paid_orders, "total_revenue": float(revenue or 0)}

@router.get("/orders")
def admin_orders(page: int = 1, limit: int = 20, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    q = db.query(Order).order_by(Order.id.desc())
    total = q.count()
    orders = q.offset((page-1)*limit).limit(limit).all()
    return {"items": [serialize_order(o) for o in orders], "page": page, "limit": limit,
            "total": total, "total_pages": (total+limit-1)//limit if total else 0}

@router.get("/reports")
def reports(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    most_purchased = db.query(OrderItem.product_id, OrderItem.product_name, func.sum(OrderItem.quantity).label("quantity"))        .join(Order, Order.id == OrderItem.order_id).filter(Order.status == "PAID")        .group_by(OrderItem.product_id, OrderItem.product_name).order_by(func.sum(OrderItem.quantity).desc()).limit(10).all()
    never_purchased = db.query(Product).outerjoin(OrderItem, Product.id == OrderItem.product_id)        .filter(OrderItem.id == None).all()
    orders_per_user = db.query(User.id, User.email, func.count(Order.id).label("orders"))        .outerjoin(Order, User.id == Order.user_id).group_by(User.id, User.email).order_by(func.count(Order.id).desc()).all()
    return {
        "total_revenue": float(db.query(func.coalesce(func.sum(Order.total_amount),0)).filter(Order.status=="PAID").scalar() or 0),
        "most_purchased_products": [{"product_id": x.product_id, "product_name": x.product_name, "quantity": int(x.quantity)} for x in most_purchased],
        "products_never_purchased": [{"id": p.id, "name": p.name} for p in never_purchased],
        "orders_per_user": [{"user_id": x.id, "email": x.email, "orders": int(x.orders)} for x in orders_per_user]
    }
