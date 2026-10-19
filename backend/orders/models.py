from django.conf import settings
from django.db import models

from products.models import Product

# Create your models here.


STATUS_CHOICES = (
    ("PENDING", "Pending"),
    ("PAID", "Paid"),
    ("SHIPPED", "Shipped"),
    ("DELIVERED", "Delivered"),
    ("CANCELLED", "Cancelled"),
)


class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders"
    )
    status = models.CharField(choices=STATUS_CHOICES, max_length=20, default="PENDING")
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    idempotency_key = models.CharField(max_length=64, null=True, blank=True)
    
    class Meta:
        indexes = [models.Index(fields=["user", "status"])]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "idempotency_key"], name="uniq_order_user_idempotency_key"
            )
        ]
    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


class OrderItem(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="order_items"
    )
    size = models.CharField(blank=True,null=True)
    color = models.CharField(null=True,blank=True)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    product_name = models.CharField(max_length=130)
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.PROTECT, related_name="payment")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    reference = models.CharField(max_length=64, unique=True)
    status = models.CharField(max_length=20, default="SUCCEEDED")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.reference} for Order #{self.order_id}"
