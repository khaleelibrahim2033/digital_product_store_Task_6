def auth(token): return {"Authorization": f"Bearer {token}"}

def test_register(client):
    r = client.post("/auth/register", json={"email":"new@test.com","password":"secret123","full_name":"New User"})
    assert r.status_code == 201
    assert "access_token" in r.json()

def test_duplicate_email(client):
    r = client.post("/auth/register", json={"email":"new@test.com","password":"secret123","full_name":"New User"})
    assert r.status_code == 400

def test_login(client):
    r = client.post("/auth/login", json={"email":"new@test.com","password":"secret123"})
    assert r.status_code == 200
    assert r.json()["token_type"] == "bearer"

def test_invalid_login(client):
    r = client.post("/auth/login", json={"email":"new@test.com","password":"wrong"})
    assert r.status_code == 401

def test_unauthorized_profile(client):
    assert client.get("/auth/profile").status_code == 401

def test_product_creation(client, admin_token):
    r = client.post("/products", headers=auth(admin_token), json={"name":"Test Product","description":"x","price":10})
    assert r.status_code == 201
    assert r.json()["name"] == "Test Product"

def test_product_listing_and_pagination(client):
    r = client.get("/products?page=1&limit=2")
    assert r.status_code == 200
    assert len(r.json()["items"]) <= 2
    assert "total_pages" in r.json()

def test_cart_operation(client, user_token, admin_token):
    p = client.post("/products", headers=auth(admin_token), json={"name":"Cart Product","price":5}).json()
    r = client.post("/cart/items", headers=auth(user_token), json={"product_id":p["id"],"quantity":2})
    assert r.status_code == 201
    assert r.json()["total_amount"] == 10

def test_empty_cart_checkout(client, user_token):
    r = client.post("/payments/create-checkout-session", headers=auth(user_token))
    assert r.status_code == 400

def test_checkout_creates_order(client, user_token, admin_token):
    p = client.post("/products", headers=auth(admin_token), json={"name":"Pay Product","price":12.5}).json()
    client.post("/cart/items", headers=auth(user_token), json={"product_id":p["id"],"quantity":1})
    r = client.post("/payments/create-checkout-session", headers=auth(user_token))
    assert r.status_code == 200
    assert r.json()["order_id"] > 0
    order = client.get(f"/orders/{r.json()['order_id']}", headers=auth(user_token))
    assert order.status_code == 200
