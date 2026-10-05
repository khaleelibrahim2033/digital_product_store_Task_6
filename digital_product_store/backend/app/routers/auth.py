from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Cart
from ..schemas import RegisterRequest, LoginRequest, TokenOut, UserOut
from ..auth import hash_password, verify_password, create_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenOut, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email.lower()).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=data.email.lower(), hashed_password=hash_password(data.password), full_name=data.full_name)
    db.add(user); db.flush()
    db.add(Cart(user_id=user.id))
    db.commit(); db.refresh(user)
    return {"access_token": create_token(user), "user": user}

@router.post("/login", response_model=TokenOut)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.lower()).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": create_token(user), "user": user}

@router.get("/profile", response_model=UserOut)
def profile(user: User = Depends(get_current_user)):
    return user
