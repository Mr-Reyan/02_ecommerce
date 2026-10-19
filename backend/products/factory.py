import factory
from django.contrib.auth import get_user_model
from factory import Faker

from authen.models import Tenant
from products.models import Category, Product, Tag

User = get_user_model()


class TenantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tenant

    name = Faker("company")


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Category {n}")
    description = Faker("sentence")


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag

    name = factory.Sequence(lambda n: f"Tag {n}")


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = Faker("word")
    description = Faker("paragraph")
    price = Faker("pydecimal", left_digits=4, right_digits=2, positive=True)

    tenant = factory.SubFactory(TenantFactory)
    category = factory.SubFactory(CategoryFactory)

    image = Faker("image_url")

    is_featured = False
    is_active = True

    sku = factory.Sequence(lambda n: f"SKU-{n}")

    specifications = {"color": "black", "brand": "Redragon", "warranty": "1 year"}

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for tag in extracted:
                self.tags.add(tag)
