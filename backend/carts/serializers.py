from rest_framework.serializers import ModelSerializer

from products.serializers import ProductReadSerializer

from .models import Cart, CartItem


class CartItemSerializer(ModelSerializer):
    product = ProductReadSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "quantity",
            "created_at",
            'size',
            'color'
        ]


class CartSerializer(ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = [
            "id",
            "user",
            "items",
            "created_at",
            "updated_at",
            "is_deleted",
        ]
