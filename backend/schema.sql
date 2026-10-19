-- E-commerce Store - PostgreSQL schema (hand-derived from the Django models).
-- Source of truth is the Django migrations: verify with `python manage.py sqlmigrate <app> 0001`
-- or `pg_dump --schema-only <db>`. Django's built-in tables (sessions, permissions, groups) are omitted.

CREATE TABLE authen_tenant (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(200) NOT NULL
);

CREATE TABLE authen_user (               -- extends Django AbstractUser
  id BIGSERIAL PRIMARY KEY,
  password VARCHAR(128) NOT NULL,
  username VARCHAR(150) NOT NULL UNIQUE,
  email VARCHAR(254) NOT NULL DEFAULT '',
  is_staff BOOLEAN NOT NULL DEFAULT FALSE,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
  date_joined TIMESTAMPTZ NOT NULL DEFAULT now(),
  tenant_id BIGINT REFERENCES authen_tenant(id) ON DELETE CASCADE
);
CREATE INDEX authen_user_tenant_idx ON authen_user(tenant_id);

CREATE TABLE products_category (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  description TEXT NOT NULL DEFAULT '',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE products_tag (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE products_product (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(130) NOT NULL,
  description TEXT NOT NULL DEFAULT '',
  price NUMERIC(10,2) NOT NULL,                 -- GAP D-09: add CHECK (price >= 0)
  tenant_id BIGINT NOT NULL REFERENCES authen_tenant(id) ON DELETE CASCADE,
  category_id BIGINT NOT NULL REFERENCES products_category(id) ON DELETE RESTRICT,
  is_featured BOOLEAN NOT NULL DEFAULT FALSE,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  sku VARCHAR(50) NOT NULL UNIQUE,
  is_deleted BOOLEAN NOT NULL DEFAULT FALSE,    -- soft delete
  specifications JSONB,                         -- e.g. {"color":"red","size_stock":{"M":5,"L":3}}
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX product_featured_idx ON products_product(is_featured);
CREATE INDEX product_active_idx   ON products_product(is_active);
CREATE INDEX product_deleted_idx  ON products_product(is_deleted);
CREATE INDEX product_price_idx    ON products_product(price);
CREATE INDEX product_specs_gin    ON products_product USING GIN (specifications);
CREATE INDEX active_products_idx  ON products_product(category_id, price)
  WHERE is_active AND NOT is_deleted;

CREATE TABLE products_product_tags (
  id BIGSERIAL PRIMARY KEY,
  product_id BIGINT NOT NULL REFERENCES products_product(id) ON DELETE CASCADE,
  tag_id BIGINT NOT NULL REFERENCES products_tag(id) ON DELETE CASCADE,
  UNIQUE (product_id, tag_id)
);

CREATE TABLE products_productimage (
  id BIGSERIAL PRIMARY KEY,
  product_id BIGINT NOT NULL REFERENCES products_product(id) ON DELETE CASCADE,
  image VARCHAR(100) NOT NULL,                  -- path under MEDIA_ROOT/products/
  position SMALLINT NOT NULL DEFAULT 0 CHECK (position >= 0)
);

CREATE TABLE inventory_inventory (
  id BIGSERIAL PRIMARY KEY,
  product_id BIGINT NOT NULL UNIQUE REFERENCES products_product(id) ON DELETE CASCADE,  -- 1:1
  stock INTEGER NOT NULL CHECK (stock >= 0),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE carts_cart (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL UNIQUE REFERENCES authen_user(id) ON DELETE CASCADE,         -- 1:1
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE carts_cartitem (
  id BIGSERIAL PRIMARY KEY,
  cart_id BIGINT NOT NULL REFERENCES carts_cart(id) ON DELETE CASCADE,
  product_id BIGINT NOT NULL REFERENCES products_product(id) ON DELETE RESTRICT,
  size VARCHAR,
  color VARCHAR,
  quantity INTEGER NOT NULL CHECK (quantity >= 0),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT unique_product_per_cart UNIQUE (cart_id, product_id)
);

CREATE TABLE orders_order (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES authen_user(id) ON DELETE RESTRICT,
  status VARCHAR(20) NOT NULL DEFAULT 'PENDING',   -- PENDING|PAID|SHIPPED|DELIVERED|CANCELLED
  total_price NUMERIC(10,2) NOT NULL,
  idempotency_key VARCHAR(64),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uniq_order_user_idempotency_key UNIQUE (user_id, idempotency_key)
);
CREATE INDEX orders_order_user_status_idx ON orders_order(user_id, status);

CREATE TABLE orders_orderitem (
  id BIGSERIAL PRIMARY KEY,
  order_id BIGINT NOT NULL REFERENCES orders_order(id) ON DELETE CASCADE,
  product_id BIGINT NOT NULL REFERENCES products_product(id) ON DELETE RESTRICT,
  product_name VARCHAR(130) NOT NULL,              -- snapshot
  size VARCHAR, color VARCHAR,
  price_at_purchase NUMERIC(10,2) NOT NULL,        -- snapshot
  quantity INTEGER NOT NULL CHECK (quantity >= 0),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE orders_payment (
  id BIGSERIAL PRIMARY KEY,
  order_id BIGINT NOT NULL UNIQUE REFERENCES orders_order(id) ON DELETE RESTRICT,      -- 1:1
  amount NUMERIC(10,2) NOT NULL,
  currency VARCHAR(3) NOT NULL,
  reference VARCHAR(64) NOT NULL UNIQUE,
  status VARCHAR(20) NOT NULL DEFAULT 'SUCCEEDED',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);