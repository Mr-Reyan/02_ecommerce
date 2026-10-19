from rest_framework import serializers
from django.db import transaction
from .models import Category, Product, Tag, ProductImage
from inventory.serializers import InventoryReadSerializer

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"



class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'

    # def validate(self, attrs):
    #     product = self.context['product']

    #     if product.images.count()>=4:
    #         raise serializers.ValidationError(
    #             "A product can have maximum of 4 images."
    #         )
    #     return attrs

class ProductReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    stock = InventoryReadSerializer(read_only=True)
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "tenant",
            "category",
            'stock',
            "tags",
            'images',
            "is_featured",
            "is_active",
            "sku",
            "is_deleted",
            "specifications",
            "updated_at",
            "created_at",
        ]

class ProductWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields = ["tenant"]

