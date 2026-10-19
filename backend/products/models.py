from django.contrib.postgres.indexes import GinIndex
from django.db import models
from django.db.models import Q

from authen.models import Tenant


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, max_length=200)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_deleted = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=130)
    description = models.TextField(max_length=400, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="products"
    )

    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products"
    )

    tags = models.ManyToManyField(Tag, related_name="products")
    image = models.URLField(blank=True)

    is_featured = models.BooleanField(default=False, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    sku = models.CharField(max_length=50, unique=True)
    is_deleted = models.BooleanField(default=False, db_index=True)
    specifications = models.JSONField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            GinIndex(fields=["specifications"]),
            models.Index(fields=["price"]),
            models.Index(
                fields=["category", "price"],
                condition=Q(is_active=True, is_deleted=False),
                name="active_products_idx",
            ),
        ]

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='images')
    image = models.ImageField(upload_to='products/')
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return f"{self.position} - {self.product.id}"