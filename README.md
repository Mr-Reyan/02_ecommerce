# E-commerce Store (Django REST API)

Weekend 1 - FalconXoft intern evaluation, project 02.

## Purpose
Multi-tenant e-commerce backend: users sign up and log in, browse a tenant's product catalogue, fill a cart, and check out with a mock payment. Stock is reduced atomically and orders are recorded with a payment.

## Tech stack
Python 3.13, Django 5.2, Django REST Framework, SimpleJWT (cookie-based), PostgreSQL (JSONB + GIN), Redis (product list cache), drf-spectacular (Swagger), pytest + pytest-django.

## Scope (implemented)
Auth (signup/login/refresh/logout/status) - product catalogue with search, filters, ordering, pagination, soft delete - inventory (total and per-size stock) - cart - idempotent atomic checkout with mock gateway - order history - Redis caching with invalidation.

## Assumptions
Every new user joins default tenant id=2; one cart per user; one cart line per product (size/colour stored on the line); currency from `STORE_CURRENCY`; payment is a mock gateway (tokens `tok_success`, `tok_declined`, `tok_insufficient_funds`, `tok_timeout`).

## Architecture summary
See `02_architecture.pdf`. Client -> Django/DRF apps (authen, products, inventory, carts, orders) -> PostgreSQL; Redis caches product lists; checkout calls the in-process mock gateway inside one DB transaction.

## Setup / run / test  (replace values to match your repo)
```bash
git clone <REPO_URL> && cd <repo>
python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                  # fill the variables below (no secrets in git)
python manage.py migrate
python manage.py shell -c "from authen.models import Tenant; Tenant.objects.get_or_create(id=2, defaults={'name':'Default'})"
python manage.py createsuperuser
python manage.py runserver                            # API on :8000, Swagger on /api/docs/
pytest                                                # runs the automated test suite (needs PostgreSQL)
```
Environment variable names (confirm against your settings.py): `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `REDIS_URL` (or host/port), `STORE_CURRENCY`.

## Testing
149 automated tests, see `05_test-cases.xlsx` (111 pass, 15 fail = real defects, 23 blocked by test-setup errors awaiting re-run).

## Known gaps (honest list)
No role-based access (any user can edit products/stock, D-07); inventory API not tenant-scoped (D-06); first add-to-cart does not check stock (D-04); deleted products can be checked out (D-08); weak passwords accepted (D-01); signup depends on tenant id=2 (D-02); `/status/` returns 401 on expired cookie (D-03); negative prices accepted (D-09); order status transitions (SHIPPED/DELIVERED/CANCELLED) exist as values but have no API; cookies use `secure=False`; Docker, CI/CD, monitoring, real payment provider not implemented; rate-limiter tests are blocked and the limiter is not part of the files reviewed. Details in `06_engineering-decisions.md`.