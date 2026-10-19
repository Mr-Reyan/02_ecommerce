import json
from decimal import Decimal

from django.conf import settings
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response

from carts.models import Cart
from config.redis_client import redis_client
from inventory.models import Inventory

from .mock_gateway import PaymentGatewayError, charge
from .models import Order, OrderItem, Payment
from .serializers import OrderSerializer


class CheckoutError(Exception):
    """Raised inside the transaction so everything rolls back."""

    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status


def _order_response(order, status):
    return Response(
        {
            "message": "Order placed successfully!",
            "order_id": order.id,
            "total_price": float(order.total_price),
        },
        status=status,
    )


@api_view(["POST"])
def checkout_order(request):
    # Duplicate/retry protection: the client sends one key per checkout attempt
    idem_key = request.headers.get("Idempotency-Key")
    if not idem_key:
        return Response({"error": "Idempotency-Key header is required."}, status=400)

    existing = Order.objects.filter(user=request.user, idempotency_key=idem_key).first()
    if existing:
        return _order_response(existing, 200)  # same request again: no new order, no new charge

    cart = get_object_or_404(Cart, user=request.user)
    items = list(cart.items.select_related("product").order_by("product_id"))
    if not items:
        return Response({"error": "Your cart is empty."}, status=400)

    payment_token = request.data.get("payment_token", "tok_success")
    currency = settings.STORE_CURRENCY

    try:
        with transaction.atomic():
            order = Order.objects.create(
                user=request.user, total_price=0, idempotency_key=idem_key
            )
            total = Decimal("0")

            for item in items:
                inventory = get_object_or_404(
                    Inventory.objects.select_for_update(), product=item.product
                )

                if inventory.stock < item.quantity:
                    raise CheckoutError(f"{item.product.name} is out of stock.")

                if item.product.specifications and "size_stock" in item.product.specifications:
                    specs = dict(item.product.specifications)
                    size_stock = dict(specs.get("size_stock", {}))
                    if item.size and item.size in size_stock:
                        if size_stock[item.size] < item.quantity:
                            raise CheckoutError(
                                f"{item.product.name} (Size: {item.size}) has only "
                                f"{size_stock[item.size]} left in stock."
                            )
                        size_stock[item.size] -= item.quantity
                        specs["size_stock"] = size_stock
                        item.product.specifications = specs
                        item.product.save(update_fields=["specifications"])

                inventory.stock -= item.quantity
                inventory.save()

                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    price_at_purchase=item.product.price,
                    quantity=item.quantity,
                    product_name=item.product.name,
                    color=item.color,
                    size=item.size,
                )
                total += item.quantity * item.product.price

            try:
                result = charge(total, currency, payment_token)
            except PaymentGatewayError:
                raise CheckoutError("Payment service unavailable. Please try again.", 503)
            if not result.success:
                raise CheckoutError(f"Payment failed: {result.failure_reason}", 402)

            Payment.objects.create(
                order=order,
                amount=total,
                currency=currency,
                reference=result.reference,
                status="SUCCEEDED",
            )
            order.total_price = total
            order.status = "PAID"
            order.save()
            cart.items.all().delete()

    except CheckoutError as e:
        # The atomic block has rolled back: no order, stock unchanged, cart untouched
        return Response({"error": e.message}, status=e.status)
    except IntegrityError:
        # Two identical requests raced; the unique constraint rejected the second one
        existing = Order.objects.filter(user=request.user, idempotency_key=idem_key).first()
        if existing:
            return _order_response(existing, 200)
        raise

    # Clear product cache after checkout
    try:
        tenant_id = getattr(request.user.tenant, "id", "")
        for key in redis_client.scan_iter(match=f"products:{tenant_id}*"):
            redis_client.delete(key)
    except Exception:
        pass

    return _order_response(order, 201)


@api_view(["GET"])
def get_orders(request):
    orders = (
        Order.objects.filter(user=request.user)
        .prefetch_related("items__product__images")
        .order_by("-created_at")
    )
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data, status=200)