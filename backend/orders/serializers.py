from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    product_image = serializers.SerializerMethodField()
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "price_at_purchase",
            "quantity",
            "size",
            "color",
            "product_image",
            "line_total",
            "created_at",
        ]

    def get_product_image(self, obj):
        if obj.product:
            first_img = obj.product.images.first()
            if first_img and first_img.image:
                return first_img.image.url if hasattr(first_img.image, "url") else str(first_img.image)
            return obj.product.image
        return None

    def get_line_total(self, obj):
        return float(obj.price_at_purchase * obj.quantity)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "total_price",
            "item_count",
            "items",
            "created_at",
            "updated_at",
        ]

    def get_item_count(self, obj):
        return sum(item.quantity for item in obj.items.all())
