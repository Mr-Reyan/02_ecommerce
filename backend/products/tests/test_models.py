
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from authen.models import Tenant
from products.factory import CategoryFactory, ProductFactory, TagFactory
from products.models import Product

User = get_user_model()


def test_delete_product(db):

    tenant = Tenant.objects.create(name="TEST 1")

    user = User.objects.create_user(username="reyan", password="123", tenant=tenant)

    client = APIClient()
    client.force_authenticate(user=user)

    tag1 = TagFactory()
    tag2 = TagFactory()

    product = ProductFactory(
        tenant=tenant,
        tags=[tag1, tag2],
    )

    response = client.delete(f"/products/{product.id}/")
    product.refresh_from_db()
    assert response.status_code == 204
    assert product.is_deleted is True


def test_create_product(db):

    tenant = Tenant.objects.create(name="TEST 1")

    user = User.objects.create_user(username="reyan", password="123", tenant=tenant)

    client = APIClient()
    client.force_authenticate(user=user)

    tag1 = TagFactory()
    tag2 = TagFactory()

    category = CategoryFactory()

    response = client.post(
        "/products/",
        {
            "name": "Keyboard",
            "description": "Mechanical keyboard",
            "price": 2500.00,
            "category": category.id,
            "tags": [tag1.id, tag2.id],
            "image": "https://example.com/image.jpg",
            "is_featured": False,
            "sku": "KB-001",
            "specifications": {"color": "Black"},
        },
        format="json",
    )

    assert response.status_code == 201, response.data

    assert Product.objects.count() == 1

    product = Product.objects.first()

    assert product.name == "Keyboard"
    assert product.price == 2500.00
    assert product.sku == "KB-001"
    assert product.description == "Mechanical keyboard"
    assert product.tenant == tenant
    assert product.specifications == {"color": "Black"}


def test_delete_product(db):
    tenant = Tenant.objects.create(name="TEST 1")

    user = User.objects.create_user(username="reyan", password="123", tenant=tenant)

    client = APIClient()
    client.force_authenticate(user=user)

    tag1 = TagFactory()
    tag2 = TagFactory()

    category = CategoryFactory()

    response = client.post(
        "/products/",
        {
            "name": "Keyboard",
            "description": "Mechanical keyboard",
            "price": 2500.00,
            "category": category.id,
            "tags": [tag1.id, tag2.id],
            "image": "https://example.com/image.jpg",
            "is_featured": False,
            "sku": "KB-001",
            "specifications": {"color": "Black"},
        },
        format="json",
    )
    assert response.status_code == 201
    product = Product.objects.first()
    response = client.delete(f"/products/{product.id}/")
    assert response.status_code == 204


# def test_create_product(db):
#     tenant = Tenant.objects.create(
#             name="TEST 1"
#     )
#     user = User.objects.create_user(
#         username="reyan",
#         password="123",
#         tenant=tenant)

#     client = APIClient()
#     client.force_authenticate(user=user)

#     response = client.get("/inventory/")

#     assert response.status_code == 200

# @patch("authen.utils.requests.get")
# def test_get_user(mock_get):

#     mock_get.return_value.json.return_value = {
#         "id": 1,
#         "name": "Reyan"
#     }

#     data = get_user()

#     assert data["name"] == "Reyan"
