import os
os.environ["DATABASE_URL"] = "sqlite:///./test_store.db"
os.environ["SECRET_KEY"] = "test-secret"
os.environ["STRIPE_SECRET_KEY"] = ""
os.environ["STRIPE_WEBHOOK_SECRET"] = ""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

@pytest.fixture(scope="session", autouse=True)
def db_setup():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def user_token(client):
    r = client.post("/auth/register", json={"email":"user@test.com","password":"secret123","full_name":"Test User"})
    if r.status_code == 201:
        return r.json()["access_token"]
    return client.post("/auth/login", json={"email":"user@test.com","password":"secret123"}).json()["access_token"]

@pytest.fixture
def admin_token(client):
    r = client.post("/auth/register", json={"email":"admin@test.com","password":"secret123","full_name":"Admin"})
    from app.database import SessionLocal
    from app.models import User
    db = SessionLocal()
    u = db.query(User).filter(User.email=="admin@test.com").first()
    u.role = "admin"; db.commit(); db.close()
    return client.post("/auth/login", json={"email":"admin@test.com","password":"secret123"}).json()["access_token"]
