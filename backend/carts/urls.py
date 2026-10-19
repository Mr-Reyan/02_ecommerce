from django.urls import path

from .views import *

urlpatterns = [
    path("cart/add/", add_to_cart),
    path("cart/", get_cart),
    path("cart/items/<int:product_id>/", update_cart_quantity),
    path("cart/<int:product_id>/", remove_cart_item),
]
