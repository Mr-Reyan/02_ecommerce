from django.db import models

from products.models import Product

# Create your models here.


class Inventory(models.Model):
    product = models.OneToOneField(
        Product, on_delete=models.CASCADE, related_name="stock"
    )
    stock = models.PositiveIntegerField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} ({self.stock})"
