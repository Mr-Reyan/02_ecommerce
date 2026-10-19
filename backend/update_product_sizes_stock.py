import os
import random
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from products.models import Product
from inventory.models import Inventory
from config.redis_client import redis_client

standard_sizes = ["Small", "Medium", "Large", "X-Large"]
pant_sizes = ["28", "30", "32", "34", "36"]

products = Product.objects.all()
print(f"Updating {products.count()} products with size stock data...")

for idx, product in enumerate(products, start=1):
    specs = product.specifications or {}
    is_pant = product.category.name in ["Cargo & Pants", "Baggy Trousers"] if product.category else False
    sizes_list = pant_sizes if is_pant else standard_sizes

    # Generate realistic per-size stock
    # Guarantee at least some items have 0 stock on certain sizes (e.g. Small or X-Large)
    size_stock = {}
    for s_idx, s in enumerate(sizes_list):
        if (idx + s_idx) % 4 == 0:
            size_stock[s] = 0  # Out of stock
        elif (idx + s_idx) % 3 == 0:
            size_stock[s] = random.randint(3, 8)  # Low stock
        else:
            size_stock[s] = random.randint(10, 25)

    specs["sizes"] = sizes_list
    specs["size_stock"] = size_stock
    product.specifications = specs
    product.save(update_fields=["specifications"])

    total_stock = sum(size_stock.values())
    inv, _ = Inventory.objects.get_or_create(product=product, defaults={"stock": total_stock})
    inv.stock = total_stock
    inv.save()

# Clear redis cache
try:
    for key in redis_client.scan_iter(match="products:*"):
        redis_client.delete(key)
    print("Redis cache cleared.")
except Exception as e:
    print("Redis clear error:", e)

print("Product size stock update completed successfully.")
