# API / Screenshot Checklist

Use Swagger at `http://127.0.0.1:8000/docs`.

1. POST `/auth/register` — 201
2. POST `/auth/login` — 200
3. GET `/auth/profile` with Bearer token — 200
4. GET `/products?page=1&limit=2&search=Python` — 200
5. POST `/products` as admin — 201
6. POST `/cart/items` as user — 201
7. GET `/cart` — 200
8. POST `/payments/create-checkout-session` — 200
9. Complete Stripe test payment
10. Stripe CLI shows `checkout.session.completed`
11. GET `/orders` — order should become PAID after webhook
12. GET `/admin/stats` as admin — 200
13. GET `/admin/reports` as admin — 200
14. Run `pytest -q` — all tests pass
