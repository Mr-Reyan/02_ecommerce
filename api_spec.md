# API Specification - E-commerce Store

Base URL (local): `http://localhost:8000`. Interactive docs: `/api/docs/` (Swagger), schema: `/api/schema/` (drf-spectacular).
Auth: JWT stored in httpOnly cookies `access` (15 min) and `refresh` (7 days) set by `/login/`.
Field names marked `*` are inferred from the views/tests - confirm against serializers. Defect IDs (D-xx) are in `05_test-cases.xlsx`.

| Method | Route | Auth | Purpose | Success | Errors |
|---|---|---|---|---|---|
| POST | /signup/ | none | Register user in default tenant | 201 | 400 validation/duplicate; 500 no tenant id=2 (D-02) |
| POST | /login/ | none | Set access+refresh cookies | 200 | 400, 401 |
| POST | /token/refresh/ | refresh cookie | New access cookie | 200 | 401 missing/invalid |
| POST | /logout/ | - | Clear cookies | 200 | - |
| GET | /status/ | cookie | `{authenticated: bool}` | 200 | 401 on bad cookie (D-03) |
| GET | /products/ | yes | List (search, filters, ordering, pagination, cached) | 200 | 401/403, 404 bad page |
| POST | /products/ | yes | Create product | 201 | 400 (D-07, D-09) |
| GET/PUT/PATCH/DELETE | /products/{id}/ | yes | Retrieve / update / soft-delete | 200/204 | 404 |
| GET/POST | /inventory/ | yes | List / create stock row | 200/201 | 400 (D-05, D-06, D-07) |
| GET/PUT/PATCH/DELETE | /inventory/{id}/ | yes | Stock row operations | 200/204 | 404 |
| POST | /cart/add/ | yes | Add item | 201 | 400, 404 (D-04) |
| GET | /cart/ | yes | View cart | 200 | 401/403 |
| PATCH | /cart/items/{product_id}/ | yes | Change quantity | 200 | 400, 404 |
| DELETE | /cart/{product_id}/ | yes | Remove line | 200 | 404 |
| POST | /order/checkout/ | yes + `Idempotency-Key` header | Atomic checkout + mock payment | 201 / 200 replay | 400, 402, 404, 503 (D-08) |
| GET | /orders/ | yes | Order history | 200 | 401/403 |

Product list query params: `search`, `ordering` (`price`, `-price`, `created_at`, `-created_at`), `category`, `is_featured`, `min_price`, `max_price`, `color`, `size`, `spec_key`+`spec_value`, `page`, `page_size`.
Checkout body: `{"payment_token": "tok_success"}` (mock tokens: `tok_success`, `tok_declined`, `tok_insufficient_funds`, `tok_timeout`).
Full examples and sequence diagrams: `04_api-workflows.pdf`.