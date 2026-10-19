"""
Tests for the `carts` app: add to cart, view cart, update quantity, remove item.

Place in: carts/test_carts.py
Run:      python manage.py test carts -v 2

Test IDs (CART-xx) are in each docstring: Feature | Scenario | Expected.

BEFORE RUNNING, set the cart URL constants below to match carts/urls.py
(I could not see that file).
"""
import itertools
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from authen.models import Tenant
from carts.models import Cart, CartItem
from products.models import Category, Product
from inventory.models import Inventory

User = get_user_model()
_sku = itertools.count(1)

# TODO: match these to carts/urls.py
CART_ADD_URL = "/cart/add/"
CART_GET_URL = "/cart/"
CART_UPDATE_URL = "/cart/update/{product_id}/"
CART_REMOVE_URL = "/cart/remove/{product_id}/"


def make_product(tenant, stock=10, size_stock=None, **overrides):
    """
    stock=None  -> no inventory row is created ("inventory not configured")
    size_stock  -> e.g. {"S": 5, "M": 0, "L": 3}, stored in specifications
    """
    n = next(_sku)
    category, _ = Category.objects.get_or_create(name="Tops")
    data = {
        "name": f"Test Tee {n}",
        "price": Decimal("19.99"),
        "tenant": tenant,
        "category": category,
        "sku": f"CART-SKU-{n}",
        "is_active": True,
        "is_deleted": False,
        "specifications": {"size_stock": size_stock} if size_stock else {},
    }
    data.update(overrides)
    product = Product.objects.create(**data)
    if stock is not None:
        Inventory.objects.create(product=product, stock=stock)
    return product


class CartTestBase(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="Shop A")
        self.other_tenant = Tenant.objects.create(name="Shop B")
        self.user = User.objects.create_user(
            username="u1", password="Pass#12345", tenant=self.tenant
        )
        self.other_user = User.objects.create_user(
            username="u2", password="Pass#12345", tenant=self.tenant
        )
        self.client = APIClient()
        self.client.raise_request_exception = False  # 500s become assertable
        self.client.force_authenticate(self.user)

    # ---- request helpers
    def add(self, product, **extra):
        payload = {"product_id": product.id, **extra}
        return self.client.post(CART_ADD_URL, payload, format="json")

    def update(self, product_id, quantity):
        return self.client.patch(
            CART_UPDATE_URL.format(product_id=product_id),
            {"quantity": quantity},
            format="json",
        )

    def remove(self, product_id):
        return self.client.delete(CART_REMOVE_URL.format(product_id=product_id))

    # ---- data helpers
    def put_in_cart(self, product, quantity, size=None, user=None):
        cart, _ = Cart.objects.get_or_create(user=user or self.user)
        return CartItem.objects.create(
            cart=cart, product=product, quantity=quantity, size=size
        )

    def qty(self, product, user=None):
        item = CartItem.objects.filter(
            cart__user=user or self.user, product=product
        ).first()
        return item.quantity if item else None


# --------------------------------------------------------------------------- #
# Add to cart
# --------------------------------------------------------------------------- #
class AddToCartTests(CartTestBase):
    def test_cart01_add_valid(self):
        """CART-01 | Add | Valid product + quantity | 201, item created with that quantity"""
        p = make_product(self.tenant, stock=10)
        r = self.add(p, quantity=3)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(self.qty(p), 3)

    def test_cart02_default_quantity_is_one(self):
        """CART-02 | Add | quantity omitted | 201, quantity defaults to 1"""
        p = make_product(self.tenant, stock=10)
        self.assertEqual(self.add(p).status_code, 201)
        self.assertEqual(self.qty(p), 1)

    def test_cart03_numeric_string_quantity_accepted(self):
        """CART-03 | Add | quantity "3" (string) | 201, stored as integer 3"""
        p = make_product(self.tenant, stock=10)
        self.assertEqual(self.add(p, quantity="3").status_code, 201)
        self.assertEqual(self.qty(p), 3)

    def test_cart04_invalid_quantity_values(self):
        """CART-04 | Add | quantity 0, -1, "abc", "1.5", null | 400, nothing added"""
        p = make_product(self.tenant, stock=10)
        for bad in (0, -1, "abc", "1.5", None):
            with self.subTest(quantity=bad):
                r = self.add(p, quantity=bad)
                self.assertEqual(r.status_code, 400)
        self.assertIsNone(self.qty(p))

    def test_cart05_same_product_twice_increments(self):
        """CART-05 | Add | Same product added twice (retry) | one row, quantities summed"""
        p = make_product(self.tenant, stock=10)
        self.add(p, quantity=2)
        r = self.add(p, quantity=3)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(self.qty(p), 5)
        self.assertEqual(CartItem.objects.filter(cart__user=self.user, product=p).count(), 1)

    def test_cart06_second_add_exceeding_stock_rejected(self):
        """CART-06 | Add | Second add pushes total above stock | 400, quantity unchanged"""
        p = make_product(self.tenant, stock=5)
        self.add(p, quantity=3)
        r = self.add(p, quantity=3)
        self.assertEqual(r.status_code, 400)
        self.assertEqual(self.qty(p), 3)

    def test_cart07_quantity_equal_to_stock_boundary(self):
        """CART-07 | Add | quantity == stock | 201"""
        p = make_product(self.tenant, stock=5)
        self.assertEqual(self.add(p, quantity=5).status_code, 201)
        self.assertEqual(self.qty(p), 5)

    def test_cart08_first_add_above_stock_rejected(self):
        """CART-08 | Add | First add with quantity > stock | 400, nothing added

        Expected to FAIL today: the stock check only runs when the item
        already exists (inside `if not created`). Log as a defect.
        """
        p = make_product(self.tenant, stock=5)
        r = self.add(p, quantity=6)
        self.assertEqual(r.status_code, 400)
        self.assertIsNone(self.qty(p))

    def test_cart09_out_of_stock(self):
        """CART-09 | Add | Stock is 0 | 400, nothing added"""
        p = make_product(self.tenant, stock=0)
        r = self.add(p, quantity=1)
        self.assertEqual(r.status_code, 400)
        self.assertIsNone(self.qty(p))

    def test_cart10_inventory_not_configured(self):
        """CART-10 | Add | Product has no stock record | 400 'inventory not configured'"""
        p = make_product(self.tenant, stock=None)
        r = self.add(p, quantity=1)
        self.assertEqual(r.status_code, 400)
        self.assertIn("inventory", r.data["error"].lower())

    def test_cart11_unknown_or_missing_product(self):
        """CART-11 | Add | Non-existent / missing product_id | 404"""
        r = self.client.post(CART_ADD_URL, {"product_id": 999999}, format="json")
        self.assertEqual(r.status_code, 404)
        r = self.client.post(CART_ADD_URL, {"quantity": 1}, format="json")
        self.assertEqual(r.status_code, 404)

    def test_cart12_inactive_or_deleted_product(self):
        """CART-12 | Add | Inactive or soft-deleted product | 404"""
        inactive = make_product(self.tenant, is_active=False)
        deleted = make_product(self.tenant, is_deleted=True)
        self.assertEqual(self.add(inactive).status_code, 404)
        self.assertEqual(self.add(deleted).status_code, 404)

    def test_cart13_other_tenant_product(self):
        """CART-13 | Add | Product belongs to another tenant | 404 (tenant isolation)"""
        foreign = make_product(self.other_tenant)
        self.assertEqual(self.add(foreign).status_code, 404)
        self.assertIsNone(self.qty(foreign))

    def test_cart14_size_and_color_saved(self):
        """CART-14 | Add | size + color provided | stored on the cart item"""
        p = make_product(self.tenant, stock=10, size_stock={"L": 5})
        self.assertEqual(self.add(p, quantity=1, size="L", color="Black").status_code, 201)
        item = CartItem.objects.get(cart__user=self.user, product=p)
        self.assertEqual(item.size, "L")
        self.assertEqual(item.color, "Black")

    def test_cart15_size_out_of_stock_even_if_total_stock_available(self):
        """CART-15 | Add | Size M has 0 stock but product total is 10 | 400 'out of stock'"""
        p = make_product(self.tenant, stock=10, size_stock={"S": 5, "M": 0, "L": 3})
        r = self.add(p, quantity=1, size="M")
        self.assertEqual(r.status_code, 400)
        self.assertIn("out of stock", r.data["error"].lower())

    def test_cart16_size_stock_limit_on_repeat_add(self):
        """CART-16 | Add | Size L has 3: add 2 then add 2 | second add 400, quantity stays 2"""
        p = make_product(self.tenant, stock=10, size_stock={"L": 3})
        self.assertEqual(self.add(p, quantity=2, size="L").status_code, 201)
        self.assertEqual(self.add(p, quantity=2, size="L").status_code, 400)
        self.assertEqual(self.qty(p), 2)

    def test_cart17_unauthenticated(self):
        """CART-17 | Add | No credentials | 401 or 403"""
        p = make_product(self.tenant)
        anon = APIClient()
        anon.raise_request_exception = False
        r = anon.post(CART_ADD_URL, {"product_id": p.id}, format="json")
        self.assertIn(r.status_code, (401, 403))


# --------------------------------------------------------------------------- #
# View cart
# --------------------------------------------------------------------------- #
class GetCartTests(CartTestBase):
    def test_cart20_empty_cart(self):
        """CART-20 | View | User with no cart yet | 200, empty items list, cart auto-created"""
        r = self.client.get(CART_GET_URL)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["items"], [])
        self.assertTrue(Cart.objects.filter(user=self.user).exists())

    def test_cart21_lists_items(self):
        """CART-21 | View | Cart with items | 200, items include quantity/size/color"""
        p = make_product(self.tenant, stock=10, size_stock={"L": 5})
        self.add(p, quantity=2, size="L", color="Red")
        r = self.client.get(CART_GET_URL)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data["items"]), 1)
        item = r.data["items"][0]
        self.assertEqual(item["quantity"], 2)
        self.assertEqual(item["size"], "L")
        self.assertEqual(item["color"], "Red")

    def test_cart22_users_cannot_see_each_others_carts(self):
        """CART-22 | View | Another user's cart contents | not visible"""
        p = make_product(self.tenant, stock=10)
        self.put_in_cart(p, 2, user=self.other_user)
        r = self.client.get(CART_GET_URL)
        self.assertEqual(r.data["items"], [])

    def test_cart23_unauthenticated(self):
        """CART-23 | View | No credentials | 401 or 403

        If this fails with 500, get_cart has no permission class and the
        default permission is AllowAny. Log as a defect and add IsAuthenticated.
        """
        anon = APIClient()
        anon.raise_request_exception = False
        r = anon.get(CART_GET_URL)
        self.assertIn(r.status_code, (401, 403))


# --------------------------------------------------------------------------- #
# Update quantity
# --------------------------------------------------------------------------- #
class UpdateCartTests(CartTestBase):
    def test_cart30_update_valid(self):
        """CART-30 | Update | Valid new quantity | 200, quantity changed"""
        p = make_product(self.tenant, stock=10)
        self.put_in_cart(p, 1)
        r = self.update(p.id, 4)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.qty(p), 4)

    def test_cart31_update_to_exact_stock_boundary(self):
        """CART-31 | Update | quantity == stock | 200; stock+1 -> 400, quantity unchanged"""
        p = make_product(self.tenant, stock=5)
        self.put_in_cart(p, 1)
        self.assertEqual(self.update(p.id, 5).status_code, 200)
        self.assertEqual(self.update(p.id, 6).status_code, 400)
        self.assertEqual(self.qty(p), 5)

    def test_cart32_invalid_quantity_values(self):
        """CART-32 | Update | quantity 0, -3, "x" | 400, quantity unchanged"""
        p = make_product(self.tenant, stock=10)
        self.put_in_cart(p, 2)
        for bad in (0, -3, "x"):
            with self.subTest(quantity=bad):
                self.assertEqual(self.update(p.id, bad).status_code, 400)
        self.assertEqual(self.qty(p), 2)

    def test_cart33_product_not_in_cart(self):
        """CART-33 | Update | Product exists but is not in the user's cart | 404"""
        p = make_product(self.tenant, stock=10)
        self.assertEqual(self.update(p.id, 2).status_code, 404)

    def test_cart34_unknown_product(self):
        """CART-34 | Update | Non-existent product id | 404"""
        self.assertEqual(self.update(999999, 2).status_code, 404)

    def test_cart35_cannot_update_another_users_item(self):
        """CART-35 | Update | Other user tries to change my item | 404, my quantity unchanged"""
        p = make_product(self.tenant, stock=10)
        self.put_in_cart(p, 2)
        self.client.force_authenticate(self.other_user)
        self.assertEqual(self.update(p.id, 9).status_code, 404)
        self.assertEqual(self.qty(p), 2)

    def test_cart36_update_respects_size_stock(self):
        """CART-36 | Update | Item size L has 3 in stock | 4 -> 400, 3 -> 200"""
        p = make_product(self.tenant, stock=50, size_stock={"L": 3})
        self.put_in_cart(p, 1, size="L")
        self.assertEqual(self.update(p.id, 4).status_code, 400)
        self.assertEqual(self.update(p.id, 3).status_code, 200)

    def test_cart37_unauthenticated(self):
        """CART-37 | Update | No credentials | 401 or 403"""
        p = make_product(self.tenant)
        anon = APIClient()
        anon.raise_request_exception = False
        r = anon.patch(
            CART_UPDATE_URL.format(product_id=p.id), {"quantity": 1}, format="json"
        )
        self.assertIn(r.status_code, (401, 403))


# --------------------------------------------------------------------------- #
# Remove item
# --------------------------------------------------------------------------- #
class RemoveCartItemTests(CartTestBase):
    def test_cart40_remove_valid(self):
        """CART-40 | Remove | Item in cart | 200, item deleted"""
        p = make_product(self.tenant)
        self.put_in_cart(p, 2)
        r = self.remove(p.id)
        self.assertEqual(r.status_code, 200)
        self.assertIsNone(self.qty(p))

    def test_cart41_remove_twice_retry(self):
        """CART-41 | Remove | Same delete sent twice (retry) | 200 then 404, no crash"""
        p = make_product(self.tenant)
        self.put_in_cart(p, 1)
        self.assertEqual(self.remove(p.id).status_code, 200)
        self.assertEqual(self.remove(p.id).status_code, 404)

    def test_cart42_remove_item_not_in_cart(self):
        """CART-42 | Remove | Product not in cart | 404"""
        p = make_product(self.tenant)
        self.assertEqual(self.remove(p.id).status_code, 404)

    def test_cart43_cannot_remove_another_users_item(self):
        """CART-43 | Remove | Other user deletes my item | 404, item still there"""
        p = make_product(self.tenant)
        self.put_in_cart(p, 2)
        self.client.force_authenticate(self.other_user)
        self.assertEqual(self.remove(p.id).status_code, 404)
        self.assertEqual(self.qty(p, user=self.user), 2)

    def test_cart44_remove_item_of_deactivated_product(self):
        """CART-44 | Remove | Product deactivated after being added | 200, item removable

        Expected to FAIL today: remove_cart_item filters on is_active=True /
        is_deleted=False, so the customer is stuck with an unremovable item.
        Log as a defect (same issue exists in update_cart_quantity).
        """
        p = make_product(self.tenant)
        self.put_in_cart(p, 1)
        p.is_active = False
        p.save()
        r = self.remove(p.id)
        self.assertEqual(r.status_code, 200)
        self.assertIsNone(self.qty(p))

    def test_cart45_unauthenticated(self):
        """CART-45 | Remove | No credentials | 401 or 403"""
        p = make_product(self.tenant)
        anon = APIClient()
        anon.raise_request_exception = False
        r = anon.delete(CART_REMOVE_URL.format(product_id=p.id))
        self.assertIn(r.status_code, (401, 403))


# --------------------------------------------------------------------------- #
# Regression flow
# --------------------------------------------------------------------------- #
class CartFlowTests(CartTestBase):
    def test_cart50_add_update_view_remove_flow(self):
        """CART-50 | Regression flow | add -> update -> view -> remove -> view empty"""
        p = make_product(self.tenant, stock=10)
        self.assertEqual(self.add(p, quantity=1).status_code, 201)
        self.assertEqual(self.update(p.id, 4).status_code, 200)

        items = self.client.get(CART_GET_URL).data["items"]
        self.assertEqual([i["quantity"] for i in items], [4])

        self.assertEqual(self.remove(p.id).status_code, 200)
        self.assertEqual(self.client.get(CART_GET_URL).data["items"], [])