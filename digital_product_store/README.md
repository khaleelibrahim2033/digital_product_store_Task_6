# Digital Product Store — FastAPI + React Vite + Stripe

A one-day full-stack Digital Product Store built for evaluation of FastAPI, SQL relationships, JWT authentication, pagination, React/Vite integration, Stripe Checkout/Webhooks, Toast notifications, validation, admin functionality, and Pytest.

## Stack

### Backend
- FastAPI + Python
- SQLAlchemy
- SQLite by default; PostgreSQL/MySQL can be used by changing `DATABASE_URL`
- Pydantic
- JWT authentication
- Stripe Checkout + Webhooks
- Pytest

### Frontend
- React + Vite
- Tailwind CSS
- React Router
- Axios
- React Toastify

## Project structure

```text
digital_product_store/
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   ├── auth.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── tests/
│   ├── seed.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
├── README.md
└── .gitignore
```

## 1. Backend setup

```bash
cd backend
python -m venv venv
```

Windows:
```powershell
venv\Scripts\activate
```

macOS/Linux:
```bash
source venv/bin/activate
```

Install:
```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and update values.

Run seed:
```bash
python seed.py
```

Start API:
```bash
uvicorn app.main:app --reload --port 8000
```

Swagger:
`http://127.0.0.1:8000/docs`

Admin seed account:
- Email: `admin@example.com`
- Password: `Admin@123`

## 2. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Frontend:
`http://localhost:5173`

Set `VITE_API_URL=http://localhost:8000` in `frontend/.env`.

## 3. Stripe configuration

Create a Stripe account in test mode.

Put the test secret key in:
```env
STRIPE_SECRET_KEY=sk_test_...
```

For local webhook testing, install Stripe CLI and run:
```bash
stripe login
stripe listen --forward-to localhost:8000/payments/webhook
```

Copy the generated `whsec_...` value into:
```env
STRIPE_WEBHOOK_SECRET=whsec_...
```

Use Stripe test card:
- Card: `4242 4242 4242 4242`
- Expiry: any future date
- CVC: any 3 digits
- ZIP: any valid value

Important: the frontend success page does not mark an order paid. The backend updates payment/order status only from the Stripe webhook.

If Stripe keys are not configured, the backend has a safe local demo checkout URL so the rest of the application can still be demonstrated. Real payment evidence requires Stripe test keys + webhook.

## 4. Main API endpoints

### Auth
- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/profile`

### Products
- `GET /products?page=1&limit=10&search=python`
- `GET /products/{id}`
- `POST /products` (admin)
- `PUT /products/{id}` (admin)
- `DELETE /products/{id}` (admin)

### Cart
- `GET /cart`
- `POST /cart/items`
- `PUT /cart/items/{item_id}`
- `DELETE /cart/items/{item_id}`
- `DELETE /cart`

### Payments
- `POST /payments/create-checkout-session`
- `POST /payments/webhook`

### Orders
- `GET /orders?page=1&limit=5`
- `GET /orders/{id}`

### Admin
- `GET /admin/stats`
- `GET /admin/orders`
- `GET /admin/reports`

## 5. SQL relationships

```text
User 1 ─── 1 Cart
Cart 1 ─── N CartItem
Product 1 ─── N CartItem

User 1 ─── N Order
Order 1 ─── N OrderItem
Product 1 ─── N OrderItem
Order 1 ─── 1 Payment
```

## 6. SQL reports

`GET /admin/reports` demonstrates:
1. Total revenue
2. Most purchased products
3. Products never purchased
4. Number of orders per user

## 7. React pages

- `/login`
- `/register`
- `/products`
- `/products/:id`
- `/cart`
- `/orders`
- `/admin/products` (create/edit/delete)
- `/admin/orders`

The app uses Axios for API integration and React Toastify for success/error messages.

## 8. Tests

From `backend`:
```bash
pytest -q
```

The suite covers:
- registration
- duplicate email
- login
- invalid login
- unauthorized access
- product creation
- product listing
- pagination
- cart operation
- empty cart checkout
- checkout/order creation

## 9. HTTP status handling

- `200` successful reads/updates
- `201` successful creation
- `400` business/Stripe errors
- `401` missing/invalid authentication
- `403` non-admin accessing admin APIs
- `404` missing resources / invalid owner access
- `422` Pydantic validation errors

## 10. Submission evidence checklist

Recommended screenshots:
1. Swagger `/docs`
2. Register success
3. Login success/token
4. Product listing with pagination/search
5. Product detail
6. Cart with total
7. Stripe Checkout page in test mode
8. Successful Stripe payment
9. Stripe CLI webhook event
10. Order showing `PAID`
11. Admin statistics
12. Pytest passing

## Notes

For a production system, add Alembic migrations, stronger currency handling with integer cents/Decimal, inventory, idempotent webhook processing, CSRF/session hardening where applicable, rate limiting, structured logging, and deployment configuration. The current implementation intentionally prioritizes the one-day assignment's required functionality.
