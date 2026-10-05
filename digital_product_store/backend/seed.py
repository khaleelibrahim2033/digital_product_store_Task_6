from app.database import SessionLocal, Base, engine
from app.models import User, Product, Cart
from app.auth import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

admin = db.query(User).filter(User.email=="admin@example.com").first()
if not admin:
    admin = User(email="admin@example.com", full_name="Store Admin", hashed_password=hash_password("Admin@123"), role="admin")
    db.add(admin); db.flush(); db.add(Cart(user_id=admin.id))

if db.query(Product).count() == 0:
    products = [
        Product(name="Python Mastery E-book", description="Practical Python programming guide.", price=29.99, image_url="https://placehold.co/600x400?text=Python"),
        Product(name="FastAPI API Course", description="Build production-ready APIs with FastAPI.", price=49.99, image_url="https://placehold.co/600x400?text=FastAPI"),
        Product(name="React Vite Starter Kit", description="Reusable React + Vite starter project.", price=39.99, image_url="https://placehold.co/600x400?text=React"),
        Product(name="SQL Interview Pack", description="SQL queries and interview exercises.", price=19.99, image_url="https://placehold.co/600x400?text=SQL"),
        Product(name="Git & GitHub Guide", description="Version control from beginner to advanced.", price=14.99, image_url="https://placehold.co/600x400?text=Git"),
    ]
    db.add_all(products)
db.commit(); db.close()
print("Seed complete. Admin: admin@example.com / Admin@123")
