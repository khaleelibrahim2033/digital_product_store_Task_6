from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: str = Field(min_length=2, max_length=150)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    full_name: str
    role: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    description: str = ""
    price: float = Field(gt=0)
    image_url: str = ""
    is_active: bool = True

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=200)
    description: Optional[str] = None
    price: Optional[float] = Field(default=None, gt=0)
    image_url: Optional[str] = None
    is_active: Optional[bool] = None

class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str
    price: float
    image_url: str
    is_active: bool

class ProductList(BaseModel):
    items: List[ProductOut]
    page: int
    limit: int
    total: int
    total_pages: int

class CartItemRequest(BaseModel):
    product_id: int
    quantity: int = Field(ge=1, le=100)

class CartUpdateRequest(BaseModel):
    quantity: int = Field(ge=1, le=100)

class CartItemOut(BaseModel):
    id: int
    product_id: int
    product_name: str
    unit_price: float
    quantity: int
    subtotal: float

class CartOut(BaseModel):
    items: List[CartItemOut]
    total_amount: float

class OrderItemOut(BaseModel):
    product_id: int
    product_name: str
    unit_price: float
    quantity: int
    subtotal: float

class OrderOut(BaseModel):
    id: int
    status: str
    total_amount: float
    payment_status: str
    created_at: str
    items: List[OrderItemOut]

class OrderList(BaseModel):
    items: List[OrderOut]
    page: int
    limit: int
    total: int
    total_pages: int

class CheckoutResponse(BaseModel):
    order_id: int
    checkout_url: str

class StatsOut(BaseModel):
    total_products: int
    total_orders: int
    paid_orders: int
    total_revenue: float
