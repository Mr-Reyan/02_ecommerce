"""
Tests for the `inventory` app: stock records per product.

Place in: inventory/test_inventory.py
Run:      python manage.py test inventory -v 2

TODO: set INVENTORY_URL to wherever InventoryViewSet is routed (I could not
see inventory/urls.py).
Test IDs (INV-xx) are in each docstring: Feature | Scenario | Expected.
"""
import itertools
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import transaction
from django.test import TestCase
from rest_framework.test import APIClient

from authen.models import Tenant
from inventory.models import Inventory
from products.models import Category, Product

User = get_user_model()

INVENTORY_URL = "/inventory/"  # TODO
_sku = itertools.count(1)


def detail(pk):
    return f"{INVENTORY_URL}{pk}/"


def results(response):
    data = response.data
    return data["results"] if isinstance(data, dict) and "results" in data else data


class InventoryTestBase(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="Shop A")
        self.other_tenant = Tenant.objects.create(name="Shop B")
        self.user = User.objects.create_user(
            username="u1", password="Pass#12345", tenant=self.tenant
        )
        self.other_user = User.objects.create_user(
            username="u2", password="Pass#12345", tenant=self.other_tenant
        )
        self.category = Category.objects.create(name="Tops")
        self.client = APIClient()
        self.client.raise_request_exception = False
        self.client.force_authenticate(self.user)

    def make_product(self, tenant=None):
        n = next(_sku)
        return Product.objects.create(
            name=f"Product {n}",
            price=Decimal("10.00"),
            tenant=tenant or self.tenant,
            category=self.category,
            sku=f"INV-SKU-{n}",
        )

    def make_stock(self, stock=5, tenant=None):
        return Inventory.objects.create(product=self.make_product(tenant), stock=stock)


class InventoryCrudTests(InventoryTestBase):
    def test_inv01_list_and_retrieve(self):
        """INV-01 | Read | List and retrieve stock rows | 200, stock value returned"""
        inv = self.make_stock(stock=8)
        listing = self.client.get(INVENTORY_URL)
        one = self.client.get(detail(inv.id))
        self.assertEqual(listing.status_code, 200)
        self.assertIn(8, [row["stock"] for row in results(listing)])
        self.assertEqual(one.status_code, 200)
        self.assertEqual(one.data["stock"], 8)

    def test_inv02_create_stock_for_product(self):
        """INV-02 | Create | Stock record for product without one | 201, persisted"""
        p = self.make_product()
        r = self.client.post(INVENTORY_URL, {"product": p.id, "stock": 12}, format="json")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(Inventory.objects.get(product=p).stock, 12)

    def test_inv03_duplicate_stock_record_rejected(self):
        """INV-03 | Create | Second stock record for the same product | 400 (not 500)

        Likely to FAIL today: `product` is declared explicitly on
        InventoryWriteSerializer, so DRF skips the one-to-one uniqueness
        validator and the database raises IntegrityError (HTTP 500).
        """
        inv = self.make_stock(stock=5)
        savepoint = transaction.savepoint()  # keep the test transaction usable after a DB error
        r = self.client.post(
            INVENTORY_URL, {"product": inv.product_id, "stock": 9}, format="json"
        )
        transaction.savepoint_rollback(savepoint)
        self.assertEqual(r.status_code, 400)

    def test_inv04_stock_zero_boundary(self):
        """INV-04 | Create | stock = 0 accepted | 201"""
        p = self.make_product()
        r = self.client.post(INVENTORY_URL, {"product": p.id, "stock": 0}, format="json")
        self.assertEqual(r.status_code, 201)

    def test_inv05_invalid_stock_values(self):
        """INV-05 | Create | stock -1, "abc", 1.5, missing | 400, no row created"""
        for bad in (-1, "abc", 1.5, None):
            with self.subTest(stock=bad):
                p = self.make_product()
                payload = {"product": p.id}
                if bad is not None:
                    payload["stock"] = bad
                r = self.client.post(INVENTORY_URL, payload, format="json")
                self.assertEqual(r.status_code, 400)
                self.assertFalse(Inventory.objects.filter(product=p).exists())

    def test_inv06_unknown_product(self):
        """INV-06 | Create | product id does not exist | 400"""
        r = self.client.post(INVENTORY_URL, {"product": 999999, "stock": 1}, format="json")
        self.assertEqual(r.status_code, 400)

    def test_inv07_update_stock(self):
        """INV-07 | Update | PATCH stock | 200, persisted; negative value rejected"""
        inv = self.make_stock(stock=5)
        ok = self.client.patch(detail(inv.id), {"stock": 20}, format="json")
        bad = self.client.patch(detail(inv.id), {"stock": -3}, format="json")
        self.assertEqual(ok.status_code, 200)
        self.assertEqual(bad.status_code, 400)
        inv.refresh_from_db()
        self.assertEqual(inv.stock, 20)

    def test_inv08_delete_stock_keeps_product(self):
        """INV-08 | Delete | Delete stock record | 204, product still exists"""
        inv = self.make_stock()
        product_id = inv.product_id
        self.assertEqual(self.client.delete(detail(inv.id)).status_code, 204)
        self.assertFalse(Inventory.objects.filter(pk=inv.pk).exists())
        self.assertTrue(Product.objects.filter(pk=product_id).exists())

    def test_inv09_unknown_inventory_id(self):
        """INV-09 | Read | Non-existent id | 404"""
        self.assertEqual(self.client.get(detail(999999)).status_code, 404)


class InventorySecurityTests(InventoryTestBase):
    def test_inv20_unauthenticated(self):
        """INV-20 | Permissions | No credentials on list and create | 401 or 403"""
        anon = APIClient()
        anon.raise_request_exception = False
        p = self.make_product()
        self.assertIn(anon.get(INVENTORY_URL).status_code, (401, 403))
        r = anon.post(INVENTORY_URL, {"product": p.id, "stock": 1}, format="json")
        self.assertIn(r.status_code, (401, 403))

    def test_inv21_tenant_isolation_on_list(self):
        """INV-21 | Tenant isolation | Tenant B lists inventory | does not see tenant A's rows

        Expected to FAIL today: get_queryset() returns every Inventory row.
        Log as a defect (filter by product__tenant=request.user.tenant).
        """
        self.make_stock(stock=111, tenant=self.tenant)
        self.client.force_authenticate(self.other_user)
        r = self.client.get(INVENTORY_URL)
        self.assertNotIn(111, [row["stock"] for row in results(r)])

    def test_inv22_cannot_change_other_tenants_stock(self):
        """INV-22 | Tenant isolation | Tenant B patches tenant A's stock | 403/404, value unchanged

        Expected to FAIL today (same root cause as INV-21).
        """
        inv = self.make_stock(stock=5, tenant=self.tenant)
        self.client.force_authenticate(self.other_user)
        r = self.client.patch(detail(inv.id), {"stock": 0}, format="json")
        self.assertIn(r.status_code, (403, 404))
        inv.refresh_from_db()
        self.assertEqual(inv.stock, 5)

    def test_inv23_cannot_create_stock_for_other_tenants_product(self):
        """INV-23 | Tenant isolation | Tenant B creates stock for tenant A's product | 400/403/404

        Expected to FAIL today: the serializer accepts Product.objects.all().
        """
        foreign = self.make_product(tenant=self.tenant)
        self.client.force_authenticate(self.other_user)
        r = self.client.post(INVENTORY_URL, {"product": foreign.id, "stock": 5}, format="json")
        self.assertIn(r.status_code, (400, 403, 404))
        self.assertFalse(Inventory.objects.filter(product=foreign).exists())

    def test_inv24_customer_cannot_edit_stock(self):
        """INV-24 | Permissions | Regular (non-staff) user changes stock | 403

        Expected to FAIL today: no role check, any logged-in user can edit
        stock. Log as a defect or document as a known gap.
        """
        inv = self.make_stock(stock=5)
        self.assertFalse(self.user.is_staff)
        r = self.client.patch(detail(inv.id), {"stock": 999}, format="json")
        self.assertEqual(r.status_code, 403)