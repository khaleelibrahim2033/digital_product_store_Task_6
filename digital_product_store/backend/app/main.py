from fastapi import FastAPI
from .database import Base, engine
from .routers import auth, products, cart, orders, payments, admin

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Digital Product Store API", version="1.0.0")
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(payments.router)
app.include_router(admin.router)

@app.get("/")
def root():
    return {"message": "Digital Product Store API", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok"}
