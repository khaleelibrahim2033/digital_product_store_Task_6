from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Cart, CartItem, Product
from ..schemas import CartItemRequest, CartUpdateRequest, CartOut
from ..auth import get_current_user

router = APIRouter(prefix="/cart", tags=["Cart"])

def get_cart(user, db):
    cart = db.query(Cart).filter(Cart.user_id == user.id).first()
    if not cart:
        cart = Cart(user_id=user.id); db.add(cart); db.commit(); db.refresh(cart)
    return cart

def serialize(cart):
    items = [{"id": i.id, "product_id": i.product_id, "product_name": i.product.name,
              "unit_price": i.product.price, "quantity": i.quantity,
              "subtotal": round(i.product.price*i.quantity, 2)} for i in cart.items]
    return {"items": items, "total_amount": round(sum(x["subtotal"] for x in items), 2)}

@router.get("", response_model=CartOut)
def view_cart(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return serialize(get_cart(user, db))

@router.post("/items", response_model=CartOut, status_code=201)
def add_item(data: CartItemRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    product = db.get(Product, data.product_id)
    if not product or not product.is_active:
        raise HTTPException(status_code=404, detail="Product not found")
    cart = get_cart(user, db)
    item = db.query(CartItem).filter(CartItem.cart_id == cart.id, CartItem.product_id == product.id).first()
    if item:
        item.quantity += data.quantity
        if item.quantity > 100:
            raise HTTPException(status_code=422, detail="Maximum quantity is 100")
    else:
        cart.items.append(CartItem(product_id=product.id, quantity=data.quantity))
    db.commit(); db.refresh(cart)
    return serialize(cart)

@router.put("/items/{item_id}", response_model=CartOut)
def update_item(item_id: int, data: CartUpdateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart = get_cart(user, db)
    item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    item.quantity = data.quantity
    db.commit(); db.refresh(cart)
    return serialize(cart)

@router.delete("/items/{item_id}", response_model=CartOut)
def remove_item(item_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart = get_cart(user, db)
    item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    db.delete(item); db.commit(); db.refresh(cart)
    return serialize(cart)

@router.delete("", response_model=CartOut)
def clear_cart(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart = get_cart(user, db)
    cart.items.clear(); db.commit(); db.refresh(cart)
    return serialize(cart)
