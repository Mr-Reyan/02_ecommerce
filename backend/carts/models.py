from django.conf import settings
from django.db import models

from products.models import Product

# Create your models here.


class Cart(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id}"



class CartItem(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="cart_items"
    )
    size = models.CharField(blank=True,null=True)
    color = models.CharField(null=True,blank=True)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product"], name="unique_product_per_cart"
            )
        ]

    def __str__(self):
        return f"{self.id}"
