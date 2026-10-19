from django.contrib import admin

from carts.models import Cart
from orders.models import Order, OrderItem
from products.models import Category, Product, Tag,ProductImage

from .models import *

# Register your models here.
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Product)
admin.site.register(User)
admin.site.register(Tenant)
admin.site.register(Cart)
admin.site.register(ProductImage)
