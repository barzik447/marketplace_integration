import pytest
from django.urls import reverse


@pytest.fixture
def create_products(api_client, headers):
    url = reverse("products")

    def create_more_products(num=5):

        data = [
            {"name": "Test1", "price": 11},
            {"name": "Test2", "price": 22},
            {"name": "Test3", "price": 33},
            {"name": "Test4", "price": 44},
            {"name": "Test5", "price": 55},
        ]
        products = []

        for i in range(num):
            products.append(api_client.post(url, data=data[i], headers=headers))
        return products

    return create_more_products
