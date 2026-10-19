from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from products.models import Product

from .models import Cart, CartItem
from .serializers import CartSerializer


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)

    product_id = request.data.get("product_id")
    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True,
        is_deleted=False,
        tenant=request.user.tenant,
    )

    try:
        quantity = int(request.data.get("quantity", 1))
    except (TypeError, ValueError):
        return Response(
            {"error": "Quantity must be an integer"}, status=status.HTTP_400_BAD_REQUEST
        )

    if quantity <= 0:
        return Response(
            {"error": "Quantity must be greater than 0"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    size = request.data.get('size')
    specs = product.specifications or {}
    size_stock = specs.get('size_stock', {})
    available_stock = size_stock.get(size) if size and size in size_stock else (product.stock.stock if hasattr(product, 'stock') else 99)

    if available_stock <= 0:
        return Response(
            {"error": f"Item in size {size or 'selected'} is out of stock"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    carItem, created = CartItem.objects.get_or_create(
        product=product, cart=cart, defaults={"quantity": quantity}
    )
    if not created:
        if carItem.quantity + quantity > available_stock:
            return Response(
                {"error": f"Total quantity exceeds available stock ({available_stock})"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        carItem.quantity += quantity
    carItem.color = request.data.get('color')
    carItem.size = size
    carItem.save()

    return Response({"info": "Product added to cart"}, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def get_cart(request):
    cart, _ = Cart.objects.prefetch_related("items__product").get_or_create(user=request.user)
    serializer = CartSerializer(cart)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["PATCH"])
def update_cart_quantity(request, product_id):
    product = get_object_or_404(
        Product, id=product_id, is_active=True, is_deleted=False
    )

    try:
        quantity = int(request.data.get("quantity", 1))
    except (TypeError, ValueError):
        return Response(
            {"error": "Quantity must be an integer"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if quantity <= 0:
        return Response(
            {"error": "Quantity must be greater than 0"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    cart, _ = Cart.objects.get_or_create(user=request.user)
    cartItem = get_object_or_404(CartItem, cart=cart, product=product)

    specs = product.specifications or {}
    size_stock = specs.get('size_stock', {})
    available_stock = size_stock.get(cartItem.size) if cartItem.size and cartItem.size in size_stock else (product.stock.stock if hasattr(product, 'stock') else 99)

    if quantity > available_stock:
        return Response(
            {"error": f"Quantity exceeds available stock ({available_stock})"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    cartItem.quantity = quantity
    cartItem.save()
    return Response({"info": "Quantity updated!"}, status=status.HTTP_200_OK)


@api_view(["DELETE"])
def remove_cart_item(request, product_id):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    product = get_object_or_404(
        Product, id=product_id, is_active=True, is_deleted=False
    )

    cartItem = get_object_or_404(CartItem, cart=cart, product=product)
    cartItem.delete()
    return Response({"info": "Item removed!"}, status=status.HTTP_200_OK)
