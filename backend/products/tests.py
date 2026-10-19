"""
Tests for the `products` app: catalog list/search/filter, CRUD, soft delete,
tenant isolation and Redis list caching.

Place in: products/test_products.py
Run:      python manage.py test products -v 2

Needs a PostgreSQL test database (GinIndex + JSON has_key/contains lookups).
Redis is replaced by an in-memory fake, so no Redis server is needed.
Test IDs (PRD-xx) are in each docstring: Feature | Scenario | Expected.
"""
import fnmatch
import itertools
from decimal import Decimal
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from authen.models import Tenant
from inventory.models import Inventory
from products.models import Category, Product, Tag

User = get_user_model()

PRODUCTS_URL = "/products/"  # TODO: adjust if the router is mounted under a prefix
_sku = itertools.count(1)


def detail(pk):
    return f"{PRODUCTS_URL}{pk}/"


class FakeRedis:
    def __init__(self):
        self.store = {}

    def get(self, key):
        return self.store.get(key)

    def set(self, key, value, ex=None):
        self.store[key] = value

    def delete(self, *keys):
        for key in keys:
            self.store.pop(key, None)

    def scan_iter(self, match="*"):
        return iter([k for k in list(self.store) if fnmatch.fnmatch(k, match)])


def results(response):
    """Works whether or not the list endpoint is paginated."""
    data = response.data
    return data["results"] if isinstance(data, dict) and "results" in data else data


def names(response):
    return sorted(item["name"] for item in results(response))


class ProductTestBase(TestCase):
    def setUp(self):
        self.redis = FakeRedis()
        patcher = mock.patch("products.views.redis_client", self.redis)
        patcher.start()
        self.addCleanup(patcher.stop)

        self.tenant = Tenant.objects.create(name="Shop A")
        self.other_tenant = Tenant.objects.create(name="Shop B")
        self.user = User.objects.create_user(
            username="u1", password="Pass#12345", tenant=self.tenant
        )
        self.other_user = User.objects.create_user(
            username="u2", password="Pass#12345", tenant=self.other_tenant
        )
        self.category = Category.objects.create(name="Tops")
        self.tag = Tag.objects.create(name="summer")

        self.client = APIClient()
        self.client.raise_request_exception = False
        self.client.force_authenticate(self.user)

    def make(self, tenant=None, stock=None, **kw):
        n = next(_sku)
        data = {
            "name": f"Product {n}",
            "price": Decimal("10.00"),
            "tenant": tenant or self.tenant,
            "category": self.category,
            "sku": f"SKU-{n}",
            "specifications": {},
        }
        data.update(kw)
        product = Product.objects.create(**data)
        if stock is not None:
            Inventory.objects.create(product=product, stock=stock)
        return product

    def payload(self, **overrides):
        data = {
            "name": "New Tee",
            "description": "Soft cotton tee",
            "price": "19.99",
            "category": self.category.id,
            "tags": [self.tag.id],
            "sku": "SKU-NEW-1",
            "specifications": {"color": "red"},
        }
        data.update(overrides)
        return data


# --------------------------------------------------------------------------- #
# Listing, search, filters
# --------------------------------------------------------------------------- #
class ProductListTests(ProductTestBase):
    def test_prd01_list_returns_only_visible_own_tenant_products(self):
        """PRD-01 | List | Own active products only | other tenant, inactive, deleted hidden"""
        self.make(name="Visible")
        self.make(name="Inactive", is_active=False)
        self.make(name="Deleted", is_deleted=True)
        self.make(name="Foreign", tenant=self.other_tenant)
        r = self.client.get(PRODUCTS_URL)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(names(r), ["Visible"])

    def test_prd02_unauthenticated(self):
        """PRD-02 | List | No credentials | 401 or 403"""
        anon = APIClient()
        self.assertIn(anon.get(PRODUCTS_URL).status_code, (401, 403))

    def test_prd03_search(self):
        """PRD-03 | Search | ?search=hoodie matches name | only matching product"""
        self.make(name="Blue Tee")
        self.make(name="Red Hoodie")
        r = self.client.get(PRODUCTS_URL, {"search": "hoodie"})
        self.assertEqual(names(r), ["Red Hoodie"])

    def test_prd04_search_no_match(self):
        """PRD-04 | Search | No match | 200 with empty list"""
        self.make(name="Blue Tee")
        r = self.client.get(PRODUCTS_URL, {"search": "zzzz"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(results(r), [])

    def test_prd05_price_range_filters(self):
        """PRD-05 | Filter | min_price / max_price (inclusive) | correct subset"""
        self.make(name="Cheap", price=Decimal("5.00"))
        self.make(name="Mid", price=Decimal("15.00"))
        self.make(name="Pricey", price=Decimal("25.00"))
        self.assertEqual(names(self.client.get(PRODUCTS_URL, {"min_price": 15})), ["Mid", "Pricey"])
        self.assertEqual(names(self.client.get(PRODUCTS_URL, {"max_price": 15})), ["Cheap", "Mid"])
        r = self.client.get(PRODUCTS_URL, {"min_price": 10, "max_price": 20})
        self.assertEqual(names(r), ["Mid"])

    def test_prd06_invalid_price_filter_is_ignored(self):
        """PRD-06 | Filter | min_price=abc | 200, filter ignored, all products returned"""
        self.make(name="A")
        self.make(name="B")
        r = self.client.get(PRODUCTS_URL, {"min_price": "abc"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(names(r), ["A", "B"])

    def test_prd07_category_and_featured_filters(self):
        """PRD-07 | Filter | category id and is_featured | correct subset"""
        other_cat = Category.objects.create(name="Shoes")
        self.make(name="Tee")
        self.make(name="Sneaker", category=other_cat, is_featured=True)
        self.assertEqual(names(self.client.get(PRODUCTS_URL, {"category": other_cat.id})), ["Sneaker"])
        self.assertEqual(names(self.client.get(PRODUCTS_URL, {"is_featured": "true"})), ["Sneaker"])

    def test_prd08_color_filter_is_case_insensitive_on_query(self):
        """PRD-08 | Filter | ?color=RED matches specifications color 'red' | red product only"""
        self.make(name="Red", specifications={"color": "red"})
        self.make(name="Blue", specifications={"color": "blue"})
        r = self.client.get(PRODUCTS_URL, {"color": "RED"})
        self.assertEqual(names(r), ["Red"])

    def test_prd09_size_filter(self):
        """PRD-09 | Filter | ?size=L matches products whose size_stock has key L | L product only"""
        self.make(name="HasL", specifications={"size_stock": {"L": 2}})
        self.make(name="OnlyS", specifications={"size_stock": {"S": 1}})
        r = self.client.get(PRODUCTS_URL, {"size": "L"})
        self.assertEqual(names(r), ["HasL"])

    def test_prd10_spec_key_value_filter(self):
        """PRD-10 | Filter | spec_key + spec_value | matching product only"""
        self.make(name="Cotton", specifications={"fabric": "cotton"})
        self.make(name="Wool", specifications={"fabric": "wool"})
        r = self.client.get(PRODUCTS_URL, {"spec_key": "fabric", "spec_value": "cotton"})
        self.assertEqual(names(r), ["Cotton"])

    def test_prd11_ordering_by_price(self):
        """PRD-11 | Ordering | ?ordering=price and -price | ascending / descending"""
        self.make(name="B", price=Decimal("20.00"))
        self.make(name="A", price=Decimal("10.00"))
        asc = [i["name"] for i in results(self.client.get(PRODUCTS_URL, {"ordering": "price"}))]
        desc = [i["name"] for i in results(self.client.get(PRODUCTS_URL, {"ordering": "-price"}))]
        self.assertEqual(asc, ["A", "B"])
        self.assertEqual(desc, ["B", "A"])

    def test_prd12_pagination(self):
        """PRD-12 | Pagination | page_size=2 over 3 products | page 1 has 2, page 2 has 1

        Assumes ProductsPagination is page-number based with a page_size query param.
        """
        for i in range(3):
            self.make(name=f"P{i}")
        p1 = self.client.get(PRODUCTS_URL, {"page_size": 2, "page": 1})
        p2 = self.client.get(PRODUCTS_URL, {"page_size": 2, "page": 2})
        self.assertEqual(len(results(p1)), 2)
        self.assertEqual(len(results(p2)), 1)

    def test_prd13_page_out_of_range(self):
        """PRD-13 | Pagination | page beyond last | 404"""
        self.make()
        r = self.client.get(PRODUCTS_URL, {"page": 999})
        self.assertEqual(r.status_code, 404)


# --------------------------------------------------------------------------- #
# Retrieve / create / update / delete
# --------------------------------------------------------------------------- #
class ProductCrudTests(ProductTestBase):
    def test_prd20_retrieve_includes_stock(self):
        """PRD-20 | Retrieve | Product with inventory | 200, nested stock value present"""
        p = self.make(stock=7)
        r = self.client.get(detail(p.id))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["stock"]["stock"], 7)

    def test_prd21_retrieve_hidden_products(self):
        """PRD-21 | Retrieve | Inactive, deleted, other-tenant, unknown id | 404"""
        for product in (
            self.make(is_active=False),
            self.make(is_deleted=True),
            self.make(tenant=self.other_tenant),
        ):
            with self.subTest(product=product.id):
                self.assertEqual(self.client.get(detail(product.id)).status_code, 404)
        self.assertEqual(self.client.get(detail(999999)).status_code, 404)

    def test_prd22_create_valid(self):
        """PRD-22 | Create | Valid payload | 201, tenant taken from the user"""
        r = self.client.post(PRODUCTS_URL, self.payload(), format="json")
        self.assertEqual(r.status_code, 201)
        product = Product.objects.get(sku="SKU-NEW-1")
        self.assertEqual(product.tenant_id, self.tenant.id)
        self.assertEqual(product.price, Decimal("19.99"))

    def test_prd23_create_cannot_spoof_tenant(self):
        """PRD-23 | Create | Payload sets another tenant | ignored, product belongs to caller's tenant"""
        r = self.client.post(
            PRODUCTS_URL, self.payload(tenant=self.other_tenant.id), format="json"
        )
        self.assertEqual(r.status_code, 201)
        self.assertEqual(Product.objects.get(sku="SKU-NEW-1").tenant_id, self.tenant.id)

    def test_prd24_create_missing_required_fields(self):
        """PRD-24 | Create | Missing name / price / category / sku / tags | 400 each"""
        for field in ("name", "price", "category", "sku", "tags"):
            with self.subTest(missing=field):
                data = self.payload()
                data.pop(field)
                r = self.client.post(PRODUCTS_URL, data, format="json")
                self.assertEqual(r.status_code, 400)
                self.assertIn(field, r.data)

    def test_prd25_duplicate_sku(self):
        """PRD-25 | Create | SKU already used (retry of same request) | 201 then 400, one row"""
        first = self.client.post(PRODUCTS_URL, self.payload(), format="json")
        second = self.client.post(PRODUCTS_URL, self.payload(), format="json")
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 400)
        self.assertEqual(Product.objects.filter(sku="SKU-NEW-1").count(), 1)

    def test_prd26_price_boundaries(self):
        """PRD-26 | Create | price 99999999.99 accepted, 100000000.00 rejected | 201 / 400"""
        ok = self.client.post(
            PRODUCTS_URL, self.payload(price="99999999.99", sku="SKU-MAX"), format="json"
        )
        too_big = self.client.post(
            PRODUCTS_URL, self.payload(price="100000000.00", sku="SKU-BIG"), format="json"
        )
        self.assertEqual(ok.status_code, 201)
        self.assertEqual(too_big.status_code, 400)

    def test_prd27_negative_price_rejected(self):
        """PRD-27 | Create | price -5.00 | 400

        Expected to FAIL today: the DecimalField has no minimum, so negative
        prices are accepted. Log as a defect (add MinValueValidator).
        """
        r = self.client.post(PRODUCTS_URL, self.payload(price="-5.00"), format="json")
        self.assertEqual(r.status_code, 400)

    def test_prd28_text_length_boundaries(self):
        """PRD-28 | Create | name 130 / description 400 accepted; 131 / 401 rejected"""
        ok = self.client.post(
            PRODUCTS_URL,
            self.payload(name="n" * 130, description="d" * 400, sku="SKU-LEN-OK"),
            format="json",
        )
        self.assertEqual(ok.status_code, 201)
        long_name = self.client.post(
            PRODUCTS_URL, self.payload(name="n" * 131, sku="SKU-LEN-1"), format="json"
        )
        long_desc = self.client.post(
            PRODUCTS_URL, self.payload(description="d" * 401, sku="SKU-LEN-2"), format="json"
        )
        self.assertEqual(long_name.status_code, 400)
        self.assertEqual(long_desc.status_code, 400)

    def test_prd29_update_partial(self):
        """PRD-29 | Update | PATCH name | 200, persisted"""
        p = self.make(name="Old")
        r = self.client.patch(detail(p.id), {"name": "New"}, format="json")
        self.assertEqual(r.status_code, 200)
        p.refresh_from_db()
        self.assertEqual(p.name, "New")

    def test_prd30_cannot_modify_other_tenant_product(self):
        """PRD-30 | Update/Delete | Other tenant's product | 404, data unchanged"""
        foreign = self.make(tenant=self.other_tenant, name="Theirs")
        self.assertEqual(self.client.patch(detail(foreign.id), {"name": "Hacked"}, format="json").status_code, 404)
        self.assertEqual(self.client.delete(detail(foreign.id)).status_code, 404)
        foreign.refresh_from_db()
        self.assertEqual(foreign.name, "Theirs")
        self.assertFalse(foreign.is_deleted)

    def test_prd31_soft_delete(self):
        """PRD-31 | Delete | Delete product | 204, row kept with is_deleted=True, hidden from API"""
        p = self.make()
        self.assertEqual(self.client.delete(detail(p.id)).status_code, 204)
        p.refresh_from_db()
        self.assertTrue(p.is_deleted)
        self.assertEqual(self.client.get(detail(p.id)).status_code, 404)
        self.assertEqual(results(self.client.get(PRODUCTS_URL)), [])

    def test_prd32_delete_twice_retry(self):
        """PRD-32 | Delete | Same delete sent twice | 204 then 404"""
        p = self.make()
        self.assertEqual(self.client.delete(detail(p.id)).status_code, 204)
        self.assertEqual(self.client.delete(detail(p.id)).status_code, 404)

    def test_prd33_customer_cannot_manage_catalog(self):
        """PRD-33 | Permissions | Regular (non-staff) user creates a product | 403

        Expected to FAIL today: any authenticated user can create, edit and
        delete products. Log as a defect or document it as a known gap
        (no admin/customer roles on the catalog).
        """
        self.assertFalse(self.user.is_staff)
        r = self.client.post(PRODUCTS_URL, self.payload(), format="json")
        self.assertEqual(r.status_code, 403)


# --------------------------------------------------------------------------- #
# Caching and tenant isolation
# --------------------------------------------------------------------------- #
class ProductCacheTests(ProductTestBase):
    def test_prd40_list_response_is_cached(self):
        """PRD-40 | Cache | Second identical list is served from Redis | stale until invalidated"""
        self.make(name="First")
        first = self.client.get(PRODUCTS_URL)
        self.assertEqual(len([k for k in self.redis.store if k.startswith("products:")]), 1)
        self.make(name="Second")  # created directly in DB, bypassing cache invalidation
        second = self.client.get(PRODUCTS_URL)
        self.assertEqual(names(first), names(second))
        self.assertEqual(names(second), ["First"])

    def test_prd41_create_invalidates_cache(self):
        """PRD-41 | Cache | Creating via the API clears the tenant's cached lists | new product visible"""
        self.make(name="First")
        self.client.get(PRODUCTS_URL)
        r = self.client.post(PRODUCTS_URL, self.payload(name="Fresh"), format="json")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(names(self.client.get(PRODUCTS_URL)), ["First", "Fresh"])

    def test_prd42_delete_invalidates_cache(self):
        """PRD-42 | Cache | Deleting clears cached lists | deleted product disappears"""
        p = self.make(name="Gone")
        self.make(name="Stays")
        self.client.get(PRODUCTS_URL)
        self.client.delete(detail(p.id))
        self.assertEqual(names(self.client.get(PRODUCTS_URL)), ["Stays"])

    def test_prd43_cache_is_per_tenant(self):
        """PRD-43 | Cache | Tenant B lists after tenant A | sees only its own products"""
        self.make(name="A-product")
        self.make(name="B-product", tenant=self.other_tenant)
        self.client.get(PRODUCTS_URL)  # caches tenant A's list
        self.client.force_authenticate(self.other_user)
        self.assertEqual(names(self.client.get(PRODUCTS_URL)), ["B-product"])

    def test_prd44_redis_down_list_still_works(self):
        """PRD-44 | Cache | Redis raises on every call | list still 200 (fail-open)"""
        broken = mock.Mock()
        for method in ("get", "set", "scan_iter", "delete"):
            getattr(broken, method).side_effect = ConnectionError("redis down")
        self.make(name="Works")
        with mock.patch("products.views.redis_client", broken):
            r = self.client.get(PRODUCTS_URL)
            created = self.client.post(PRODUCTS_URL, self.payload(), format="json")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(names(r), ["Works"])
        self.assertEqual(created.status_code, 201)