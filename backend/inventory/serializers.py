from rest_framework import serializers

from products.models import Product

from .models import Inventory


class InventoryListSerializer(serializers.ListSerializer):

    def create(self, validated_data):
        inventory_products = [Inventory(**item) for item in validated_data]

        return Inventory.objects.bulk_create(inventory_products)


class InventoryWriteSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = Inventory
        fields = "__all__"
        list_serializer_class = InventoryListSerializer


class InventoryReadSerializer(serializers.ModelSerializer):
    # product = ProductReadSerializer(read_only=True)

    class Meta:
        model = Inventory
        fields = "__all__"
