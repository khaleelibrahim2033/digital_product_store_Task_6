from math import ceil
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..database import get_db
from ..models import Product, User
from ..schemas import ProductCreate, ProductUpdate, ProductOut, ProductList
from ..auth import get_current_user, require_admin

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("", response_model=ProductList)
def list_products(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100), search: str = "", db: Session = Depends(get_db)):
    q = db.query(Product).filter(Product.is_active == True)
    if search.strip():
        term = f"%{search.strip()}%"
        q = q.filter(or_(Product.name.ilike(term), Product.description.ilike(term)))
    total = q.count()
    items = q.order_by(Product.id.desc()).offset((page-1)*limit).limit(limit).all()
    return {"items": items, "page": page, "limit": limit, "total": total, "total_pages": ceil(total/limit) if total else 0}

@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product or not product.is_active:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("", response_model=ProductOut, status_code=201)
def create_product(data: ProductCreate, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    product = Product(**data.model_dump())
    db.add(product); db.commit(); db.refresh(product)
    return product

@router.put("/{product_id}", response_model=ProductOut)
def update_product(product_id: int, data: ProductUpdate, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(product, k, v)
    db.commit(); db.refresh(product)
    return product

@router.delete("/{product_id}")
def delete_product(product_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.is_active = False
    db.commit()
    return {"message": "Product deleted"}
