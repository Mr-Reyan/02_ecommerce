from django.urls import path

from .views import *

urlpatterns = [
    path("order/checkout/", checkout_order),
    path("top_customers/", top_customers),
    path("orders/", get_orders),
]
