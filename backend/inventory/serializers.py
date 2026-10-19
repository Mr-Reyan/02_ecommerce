from rest_framework import serializers

from products.models import Product

from .models import Inventory


class InventoryWriteSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = Inventory
        fields = "__all__"


class InventoryReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Inventory
        fields = "__all__"
