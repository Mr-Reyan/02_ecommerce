"""
Tests for the `orders` app: checkout, mock payment, stock deduction,
rollback on failure, idempotent retries and order history.

Place in: orders/test_orders.py
Run:      python manage.py test orders -v 2

Redis is replaced by an in-memory fake. STORE_CURRENCY is set to "usd" for
the tests. Test IDs (ORD-xx) are in each docstring:
Feature | Scenario | Expected.
"""
import fnmatch
import itertools
from decimal import Decimal
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from authen.models import Tenant
from carts.models import Cart, CartItem
from inventory.models import Inventory
from orders.models import Order, OrderItem, Payment
from products.models import Category, Product

User = get_user_model()

CHECKOUT_URL = "/order/checkout/"
ORDERS_URL = "/orders/"
_sku = itertools.count(1)


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


@override_settings(STORE_CURRENCY="usd")
class OrderTestBase(TestCase):
    def setUp(self):
        self.redis = FakeRedis()
        patcher = mock.patch("orders.views.redis_client", self.redis)
        patcher.start()
        self.addCleanup(patcher.stop)

        self.tenant = Tenant.objects.create(name="Shop A")
        self.user = User.objects.create_user(
            username="u1", password="Pass#12345", tenant=self.tenant
        )
        self.other_user = User.objects.create_user(
            username="u2", password="Pass#12345", tenant=self.tenant
        )
        self.category = Category.objects.create(name="Tops")
        self.client = APIClient()
        self.client.raise_request_exception = False
        self.client.force_authenticate(self.user)

    # ---- data helpers
    def make_product(self, price="19.99", stock=10, size_stock=None, **kw):
        n = next(_sku)
        data = {
            "name": f"Product {n}",
            "price": Decimal(price),
            "tenant": self.tenant,
            "category": self.category,
            "sku": f"ORD-SKU-{n}",
            "specifications": {"size_stock": size_stock} if size_stock else {},
        }
        data.update(kw)
        product = Product.objects.create(**data)
        if stock is not None:
            Inventory.objects.create(product=product, stock=stock)
        return product

    def fill_cart(self, *lines, user=None):
        """lines: (product, quantity) or (product, quantity, size)"""
        cart, _ = Cart.objects.get_or_create(user=user or self.user)
        for line in lines:
            product, quantity, *rest = line
            CartItem.objects.create(
                cart=cart, product=product, quantity=quantity, size=rest[0] if rest else None
            )
        return cart

    def stock(self, product):
        return Inventory.objects.get(product=product).stock

    def checkout(self, key="key-1", token=None, client=None):
        payload = {"payment_token": token} if token else {}
        extra = {"HTTP_IDEMPOTENCY_KEY": key} if key else {}
        return (client or self.client).post(CHECKOUT_URL, payload, format="json", **extra)

    def assert_nothing_changed(self, expected_stock):
        """After a failed checkout: no order/payment, stock same, cart intact."""
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(OrderItem.objects.count(), 0)
        self.assertEqual(Payment.objects.count(), 0)
        for product, stock in expected_stock.items():
            self.assertEqual(self.stock(product), stock)
        self.assertTrue(CartItem.objects.filter(cart__user=self.user).exists())


# --------------------------------------------------------------------------- #
# Checkout: success paths
# --------------------------------------------------------------------------- #
class CheckoutSuccessTests(OrderTestBase):
    def test_ord01_successful_checkout(self):
        """ORD-01 | Checkout | Two-item cart, default payment token | 201, order PAID, payment recorded, stock reduced, cart emptied"""
        a = self.make_product(price="19.99", stock=10)
        b = self.make_product(price="5.00", stock=4)
        self.fill_cart((a, 2), (b, 1))

        r = self.checkout()

        self.assertEqual(r.status_code, 201)
        order = Order.objects.get()
        self.assertEqual(r.data["order_id"], order.id)
        self.assertAlmostEqual(r.data["total_price"], 44.98, places=2)
        self.assertEqual(order.status, "PAID")
        self.assertEqual(order.total_price, Decimal("44.98"))
        self.assertEqual(order.items.count(), 2)
        payment = Payment.objects.get(order=order)
        self.assertEqual(payment.amount, Decimal("44.98"))
        self.assertEqual(payment.currency, "usd")
        self.assertEqual(payment.status, "SUCCEEDED")
        self.assertTrue(payment.reference.startswith("mock_pay_"))
        self.assertEqual(self.stock(a), 8)
        self.assertEqual(self.stock(b), 3)
        self.assertFalse(CartItem.objects.filter(cart__user=self.user).exists())

    def test_ord02_order_items_snapshot_product_data(self):
        """ORD-02 | Checkout | Order items store name, price, size, color | snapshot values saved"""
        p = self.make_product(price="12.50", size_stock={"M": 5})
        cart = self.fill_cart((p, 2, "M"))
        CartItem.objects.filter(cart=cart).update(color="Black")
        self.checkout()
        item = OrderItem.objects.get()
        self.assertEqual(item.product_name, p.name)
        self.assertEqual(item.price_at_purchase, Decimal("12.50"))
        self.assertEqual((item.size, item.color, item.quantity), ("M", "Black", 2))

    def test_ord03_price_change_after_purchase_does_not_alter_order(self):
        """ORD-03 | Checkout | Product price changes after purchase | order item keeps old price"""
        p = self.make_product(price="10.00")
        self.fill_cart((p, 1))
        self.checkout()
        p.price = Decimal("99.00")
        p.save()
        self.assertEqual(OrderItem.objects.get().price_at_purchase, Decimal("10.00"))

    def test_ord04_total_is_decimal_exact(self):
        """ORD-04 | Checkout | 3 x 19.99 | total exactly 59.97 (no float drift)"""
        p = self.make_product(price="19.99")
        self.fill_cart((p, 3))
        self.checkout()
        self.assertEqual(Payment.objects.get().amount, Decimal("59.97"))

    def test_ord05_quantity_equals_stock_boundary(self):
        """ORD-05 | Checkout | quantity == stock | 201, stock becomes 0"""
        p = self.make_product(stock=3)
        self.fill_cart((p, 3))
        self.assertEqual(self.checkout().status_code, 201)
        self.assertEqual(self.stock(p), 0)

    def test_ord06_size_stock_is_deducted(self):
        """ORD-06 | Checkout | Item with size L | size_stock[L] and total stock both reduced"""
        p = self.make_product(stock=10, size_stock={"L": 5, "S": 5})
        self.fill_cart((p, 2, "L"))
        self.assertEqual(self.checkout().status_code, 201)
        p.refresh_from_db()
        self.assertEqual(p.specifications["size_stock"], {"L": 3, "S": 5})
        self.assertEqual(self.stock(p), 8)

    def test_ord07_other_users_cart_untouched(self):
        """ORD-07 | Checkout | User 1 checks out | user 2's cart still intact"""
        p = self.make_product(stock=10)
        self.fill_cart((p, 1))
        self.fill_cart((p, 2), user=self.other_user)
        self.checkout()
        self.assertEqual(CartItem.objects.filter(cart__user=self.other_user).count(), 1)


# --------------------------------------------------------------------------- #
# Checkout: validation and rollback
# --------------------------------------------------------------------------- #
class CheckoutFailureTests(OrderTestBase):
    def test_ord10_missing_idempotency_key(self):
        """ORD-10 | Checkout | No Idempotency-Key header | 400, nothing created"""
        p = self.make_product()
        self.fill_cart((p, 1))
        r = self.checkout(key=None)
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Order.objects.count(), 0)

    def test_ord11_empty_cart(self):
        """ORD-11 | Checkout | Cart exists but has no items | 400 'cart is empty'"""
        Cart.objects.create(user=self.user)
        r = self.checkout()
        self.assertEqual(r.status_code, 400)
        self.assertIn("empty", r.data["error"].lower())

    def test_ord12_no_cart_at_all(self):
        """ORD-12 | Checkout | User never created a cart | 404"""
        self.assertEqual(self.checkout().status_code, 404)

    def test_ord13_out_of_stock_rolls_back(self):
        """ORD-13 | Checkout | quantity > stock | 400, nothing changed"""
        p = self.make_product(stock=1)
        self.fill_cart((p, 2))
        r = self.checkout()
        self.assertEqual(r.status_code, 400)
        self.assertIn("out of stock", r.data["error"].lower())
        self.assert_nothing_changed({p: 1})

    def test_ord14_second_item_fails_rolls_back_first(self):
        """ORD-14 | Checkout | Item A ok, item B out of stock | whole checkout rolled back, A's stock restored"""
        a = self.make_product(stock=10)
        b = self.make_product(stock=1)
        self.fill_cart((a, 2), (b, 5))
        r = self.checkout()
        self.assertEqual(r.status_code, 400)
        self.assert_nothing_changed({a: 10, b: 1})

    def test_ord15_size_stock_insufficient_rolls_back(self):
        """ORD-15 | Checkout | Total stock fine but size L has 1 left, wants 2 | 400, nothing changed"""
        p = self.make_product(stock=10, size_stock={"L": 1})
        self.fill_cart((p, 2, "L"))
        r = self.checkout()
        self.assertEqual(r.status_code, 400)
        self.assert_nothing_changed({p: 10})
        p.refresh_from_db()
        self.assertEqual(p.specifications["size_stock"]["L"], 1)

    def test_ord16_product_without_inventory(self):
        """ORD-16 | Checkout | Product has no stock record | 404, nothing changed"""
        p = self.make_product(stock=None)
        self.fill_cart((p, 1))
        r = self.checkout()
        self.assertEqual(r.status_code, 404)
        self.assertEqual(Order.objects.count(), 0)
        self.assertTrue(CartItem.objects.filter(cart__user=self.user).exists())

    def test_ord17_deleted_product_in_cart(self):
        """ORD-17 | Checkout | Product soft-deleted/deactivated after being added | 400, cannot be bought

        Expected to FAIL today: checkout never re-checks is_active/is_deleted,
        so removed products can still be purchased. Log as a defect.
        """
        deleted = self.make_product(stock=5)
        inactive = self.make_product(stock=5)
        self.fill_cart((deleted, 1))
        Product.objects.filter(pk=deleted.pk).update(is_deleted=True)
        self.assertEqual(self.checkout(key="k-del").status_code, 400)

        CartItem.objects.all().delete()
        self.fill_cart((inactive, 1))
        Product.objects.filter(pk=inactive.pk).update(is_active=False)
        self.assertEqual(self.checkout(key="k-inactive").status_code, 400)


# --------------------------------------------------------------------------- #
# Payment (mock gateway)
# --------------------------------------------------------------------------- #
class PaymentTests(OrderTestBase):
    def test_ord20_declined_payment_rolls_back(self):
        """ORD-20 | Payment | tok_declined, tok_insufficient_funds | 402, nothing changed"""
        p = self.make_product(stock=5)
        self.fill_cart((p, 2))
        for token in ("tok_declined", "tok_insufficient_funds"):
            with self.subTest(token=token):
                r = self.checkout(key=f"key-{token}", token=token)
                self.assertEqual(r.status_code, 402)
                self.assertIn("payment failed", r.data["error"].lower())
                self.assert_nothing_changed({p: 5})

    def test_ord21_gateway_timeout(self):
        """ORD-21 | Payment | tok_timeout (gateway down) | 503, nothing changed"""
        p = self.make_product(stock=5)
        self.fill_cart((p, 2))
        r = self.checkout(token="tok_timeout")
        self.assertEqual(r.status_code, 503)
        self.assert_nothing_changed({p: 5})

    @override_settings(STORE_CURRENCY="gbp")
    def test_ord22_unsupported_currency(self):
        """ORD-22 | Payment | Store currency not supported by gateway | 402, nothing changed"""
        p = self.make_product(stock=5)
        self.fill_cart((p, 1))
        r = self.checkout()
        self.assertEqual(r.status_code, 402)
        self.assert_nothing_changed({p: 5})

    def test_ord23_retry_same_key_after_failed_payment(self):
        """ORD-23 | Payment | Declined, then same Idempotency-Key retried with a good token | 201 (failed attempt left no order)"""
        p = self.make_product(stock=5)
        self.fill_cart((p, 1))
        self.assertEqual(self.checkout(key="retry-1", token="tok_declined").status_code, 402)
        r = self.checkout(key="retry-1", token="tok_success")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(self.stock(p), 4)


# --------------------------------------------------------------------------- #
# Idempotency / duplicate / retry
# --------------------------------------------------------------------------- #
class IdempotencyTests(OrderTestBase):
    def test_ord30_same_key_twice_creates_one_order(self):
        """ORD-30 | Idempotency | Same key sent twice | 201 then 200, same order id, one charge, stock deducted once"""
        p = self.make_product(stock=10)
        self.fill_cart((p, 2))
        first = self.checkout(key="dup-1")
        second = self.checkout(key="dup-1")
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.data["order_id"], second.data["order_id"])
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Payment.objects.count(), 1)
        self.assertEqual(self.stock(p), 8)

    def test_ord31_new_key_after_cart_emptied(self):
        """ORD-31 | Idempotency | New key after successful checkout (cart empty) | 400, no second order"""
        p = self.make_product(stock=10)
        self.fill_cart((p, 1))
        self.checkout(key="a")
        r = self.checkout(key="b")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Order.objects.count(), 1)

    def test_ord32_same_key_different_users_independent(self):
        """ORD-32 | Idempotency | Two users use the same key | each gets own order"""
        p = self.make_product(stock=10)
        self.fill_cart((p, 1))
        self.fill_cart((p, 1), user=self.other_user)
        other = APIClient()
        other.raise_request_exception = False
        other.force_authenticate(self.other_user)
        r1 = self.checkout(key="same")
        r2 = self.checkout(key="same", client=other)
        self.assertEqual((r1.status_code, r2.status_code), (201, 201))
        self.assertEqual(Order.objects.count(), 2)
        self.assertNotEqual(r1.data["order_id"], r2.data["order_id"])


# --------------------------------------------------------------------------- #
# Cache + permissions
# --------------------------------------------------------------------------- #
class CheckoutSideEffectTests(OrderTestBase):
    def test_ord40_product_cache_cleared_after_checkout(self):
        """ORD-40 | Cache | Cached product lists for the tenant | deleted after successful checkout"""
        p = self.make_product(stock=5)
        self.fill_cart((p, 1))
        self.redis.store[f"products:{self.tenant.id}:page:1"] = "cached"
        self.checkout()
        self.assertNotIn(f"products:{self.tenant.id}:page:1", self.redis.store)

    def test_ord41_redis_down_does_not_break_checkout(self):
        """ORD-41 | Cache | Redis raises during cache clearing | checkout still 201"""
        p = self.make_product(stock=5)
        self.fill_cart((p, 1))
        broken = mock.Mock()
        broken.scan_iter.side_effect = ConnectionError("redis down")
        with mock.patch("orders.views.redis_client", broken):
            r = self.checkout()
        self.assertEqual(r.status_code, 201)

    def test_ord42_unauthenticated_checkout(self):
        """ORD-42 | Permissions | Checkout without credentials | 401 or 403"""
        anon = APIClient()
        anon.raise_request_exception = False
        r = anon.post(CHECKOUT_URL, {}, format="json", HTTP_IDEMPOTENCY_KEY="k")
        self.assertIn(r.status_code, (401, 403))


# --------------------------------------------------------------------------- #
# Order history
# --------------------------------------------------------------------------- #
class OrderHistoryTests(OrderTestBase):
    def place_order(self, key, price="10.00", quantity=1, client=None, user=None):
        p = self.make_product(price=price, stock=20)
        self.fill_cart((p, quantity), user=user)
        return self.checkout(key=key, client=client), p

    def test_ord50_empty_history(self):
        """ORD-50 | History | User with no orders | 200, empty list"""
        r = self.client.get(ORDERS_URL)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data, [])

    def test_ord51_lists_own_orders_newest_first_with_items(self):
        """ORD-51 | History | Two orders | newest first, item_count, line_total, status, no image -> null"""
        first, _ = self.place_order("h1", price="10.00", quantity=2)
        second, _ = self.place_order("h2", price="5.00", quantity=3)
        r = self.client.get(ORDERS_URL)
        self.assertEqual(r.status_code, 200)
        self.assertEqual([o["id"] for o in r.data], [second.data["order_id"], first.data["order_id"]])
        newest = r.data[0]
        self.assertEqual(newest["status"], "PAID")
        self.assertEqual(newest["item_count"], 3)
        self.assertEqual(newest["items"][0]["line_total"], 15.0)
        self.assertIsNone(newest["items"][0]["product_image"])

    def test_ord52_cannot_see_other_users_orders(self):
        """ORD-52 | History | User 2 has an order | not visible to user 1"""
        other = APIClient()
        other.raise_request_exception = False
        other.force_authenticate(self.other_user)
        self.place_order("o1", client=other, user=self.other_user)
        self.assertEqual(self.client.get(ORDERS_URL).data, [])

    def test_ord53_unauthenticated(self):
        """ORD-53 | History | No credentials | 401 or 403"""
        anon = APIClient()
        anon.raise_request_exception = False
        self.assertIn(anon.get(ORDERS_URL).status_code, (401, 403))