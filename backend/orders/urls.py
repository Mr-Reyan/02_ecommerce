from django.urls import path

from .views import checkout_order, get_orders

urlpatterns = [
    path("order/checkout/", checkout_order),
    path("orders/", get_orders),
]
