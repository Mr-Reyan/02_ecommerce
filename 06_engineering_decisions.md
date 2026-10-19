# Engineering Decisions - E-commerce Store

## 1. Decisions table
| Area | Options considered | Chosen | Why | Trade-off |
|---|---|---|---|---|
| Framework | Flask, FastAPI, Django+DRF | Django + DRF | ORM, migrations, admin, auth built in; fastest path to a complete MVP | Heavier than FastAPI |
| Database | SQLite, MySQL, PostgreSQL | PostgreSQL | Row locks (`SELECT FOR UPDATE`), JSONB + GIN index, partial indexes | Needs a server to run tests |
| Auth | Sessions, JWT in localStorage, JWT in httpOnly cookies | JWT in httpOnly cookies | JavaScript cannot read the token (XSS-safe); short access + longer refresh | Needs CSRF thinking; logout does not revoke tokens |
| Multi-tenancy | Separate DBs, schema per tenant, tenant FK column | Tenant FK on user/product | Simple, one DB | Every query must filter tenant (missed in inventory, D-06) |
| Variants | Variant table (SKU per size) vs JSON | `specifications.size_stock` JSON + total stock | Fast to build, flexible attributes | No DB constraints on per-size stock; two stock numbers must stay in sync |
| Stock safety | Optimistic version field, app-level lock, row lock | `select_for_update` on inventory rows, ordered by product id | Prevents overselling; ordering avoids deadlocks | Locks held until commit |
| Checkout atomicity | Saga/compensation vs one transaction | One `transaction.atomic()` incl. mock charge | Any failure rolls back order, stock, payment record | Real gateways should not be called inside a long DB transaction |
| Duplicate protection | Client-side disable, token table, Idempotency-Key + unique constraint | `Idempotency-Key` header + `UNIQUE(user, key)` | Safe under retries and races (IntegrityError path) | Client must send a key per attempt |
| Money | float, Decimal | Decimal(10,2) + price snapshot on order items | No rounding drift (3 x 19.99 = 59.97 tested); history survives price changes | - |
| Deletion | Hard delete, soft delete | Soft delete for products | Orders keep referencing the product | Filters needed everywhere (D-08, D-11) |
| Caching | None, per-view cache, Redis keyed list | Redis keyed by tenant+all query params, TTL 300 s, delete on writes | Cheap catalogue reads | Stale up to 5 min if invalidation is missed; fail-open on Redis errors |
| Payment | Real Stripe, mock | Mock gateway with test tokens | Assignment asks for mock payment | No real money flow, webhooks, refunds |

## 2. Security
Implemented: password hashing (Django), httpOnly cookies, SameSite=Lax, tenant filter on products and cart, object lookups scoped to the user's cart/orders, unique constraints, Decimal money, parameterised ORM queries.
Known weaknesses: `secure=False` cookies (must be True behind HTTPS); no role checks on products/inventory (D-07); inventory not tenant-scoped (D-06); no password validators (D-01); logout only deletes cookies, refresh tokens are not blacklisted; no CSRF token on cookie-authenticated POSTs (SameSite helps but is not a full defence); no rate limiting in the reviewed code.

## 3. Technical risks
1. Cross-tenant data access through `/inventory/` (High). 2. Any customer can change catalogue and stock (High). 3. Overselling via first add-to-cart is blocked later at checkout, so the cart can show impossible quantities (Medium). 4. Charge succeeds but DB commit fails -> customer charged without order (needs gateway reconciliation / outbox). 5. Cache staleness for stock shown in lists. 6. Cart allows one line per product, so two sizes of the same product overwrite each other's size.

## 4. Implemented vs planned
| Item | Status |
|---|---|
| Auth, catalogue, inventory, cart, checkout, orders, Redis cache, Swagger, 149 automated tests | Implemented |
| Roles/permissions, tenant-scoped inventory, password validation, stock check on first add, active check at checkout, CHECK price>=0 | Planned (remediation, see below) |
| Order status update API (ship/deliver/cancel), refunds | Planned - statuses exist but only PENDING->PAID is used |
| Docker, CI/CD, HTTPS, object storage for images, real payment provider, Celery workers, monitoring/logging | Planned only |

## 5. Remediation of known gaps (from the Defects sheet)
| Defect | Fix |
|---|---|
| D-01 | `validate_password()` in RegisterSerializer |
| D-02 | Look up/create the default tenant by name; return clean 503/400 |
| D-03 | `@authentication_classes([])` on `/status/`; UI calls `/token/refresh/` once when false |
| D-04 | Validate quantity against available stock before `get_or_create` |
| D-05 | Add `UniqueValidator` or drop explicit `product` field in InventoryWriteSerializer |
| D-06 | `get_queryset` filters `product__tenant=request.user.tenant`; restrict product choices |
| D-07 | `IsAdminUser`/custom permission for unsafe methods on products and inventory |
| D-08 | Skip/reject inactive or deleted products in checkout |
| D-09 | `MinValueValidator(0)` + DB `CheckConstraint(price >= 0)` |
| D-10 | `.order_by("id")` on inventory queryset |
| D-11 | Look up cart item by cart+product without the active filter (confirm after re-run) |