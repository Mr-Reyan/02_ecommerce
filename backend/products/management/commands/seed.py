import random
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from authen.models import Tenant
from orders.models import Order, OrderItem
from products.models import Category, Product, Tag

User = get_user_model()


class Command(BaseCommand):
    help = "Seed database"

    def handle(self, *args, **kwargs):

        Product.objects.all().delete()
        Category.objects.all().delete()
        Tag.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()
        Tenant.objects.all().delete()

        tenant = Tenant.objects.create(name="Falcon Store")

        users = []

        for username in ["admin1", "admin2", "admin3"]:

            user = User.objects.create_user(
                username=username,
                password="2204",
                tenant=tenant,
            )

            users.append(user)

        categories = []

        for name in [
            "Laptops",
            "Phones",
            "Gaming",
            "Accessories",
            "TV",
            "Audio",
            "Wearables",
            "Storage",
        ]:

            categories.append(Category.objects.create(name=name))

        tags = []

        for name in [
            "Apple",
            "Samsung",
            "Dell",
            "HP",
            "Asus",
            "Lenovo",
            "Sony",
            "Featured",
            "Sale",
        ]:

            tags.append(Tag.objects.create(name=name))
        brands = [
            "Apple",
            "Samsung",
            "Dell",
            "HP",
            "Asus",
            "Lenovo",
            "Sony",
            "Acer",
            "MSI",
        ]

        cpus = [
            "Intel i5",
            "Intel i7",
            "Intel Ultra 9",
            "Ryzen 5",
            "Ryzen 7",
            "Apple M4",
        ]

        rams = ["8GB", "16GB", "32GB", "64GB"]

        storage = [
            "256GB",
            "512GB",
            "1TB",
            "2TB",
        ]

        for i in range(10000):

            product = Product.objects.create(
                tenant=tenant,
                name=f"Product {i}",
                description="Random generated product",
                price=Decimal(random.randint(100, 5000)),
                category=random.choice(categories),
                sku=f"SKU-{i}",
                image="https://picsum.photos/300",
                is_active=True,
                is_featured=random.choice([True, False]),
                specifications={
                    "brand": random.choice(brands),
                    "processor": random.choice(cpus),
                    "ram": random.choice(rams),
                    "storage": random.choice(storage),
                    "rating": round(random.uniform(2.5, 5.0), 1),
                    "color": random.choice(
                        [
                            "Black",
                            "White",
                            "Blue",
                            "Silver",
                        ]
                    ),
                },
            )

            product.tags.add(*random.sample(tags, random.randint(1, 3)))
            totals = [
                1200,
                1300,
                400,
            ]

        for user, total in zip(users, totals):

            order = Order.objects.create(
                user=user,
                total_price=total,
                status="DELIVERED",
            )

            products = Product.objects.order_by("?")[:10]

            for product in products:

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    quantity=random.randint(1, 2),
                    price_at_purchase=product.price,
                )

        self.stdout.write(self.style.SUCCESS("Database Seeded Successfully"))
