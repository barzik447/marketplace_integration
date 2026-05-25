import pytest
from django.urls import reverse


@pytest.fixture
def create_products(api_client, headers):
    url = reverse("products")

    products_data = [
        {"name": "Test1", "price": 11},
        {"name": "Test2", "price": 22},
        {"name": "Test3", "price": 33},
        {"name": "Test4", "price": 44},
        {"name": "Test5", "price": 55},
    ]

    def create_more_products(num=1):

        products = []

        for i in range(num):
            products.append(
                api_client.post(url, data=products_data[i], headers=headers)
            )
        return products

    return create_more_products


@pytest.fixture
def create_orders(api_client, headers, create_products):

    url = reverse("orders")

    orders_data = [
        {"description": "Order 1", "items": [{"product": None, "units": 1}]},
        {"description": "Order 2", "items": [{"product": None, "units": 2}]},
        {"description": "Order 3", "items": [{"product": None, "units": 1}]},
        {"description": "Order 4", "items": [{"product": None, "units": 3}]},
        {"description": "Order 5", "items": [{"product": None, "units": 2}]},
    ]

    def create_more_orders(num=1):
        products = [p.json() for p in create_products(num=num)]
        orders = []
        for i in range(num):
            body = orders_data[i].copy()
            body["items"] = [
                {"product": products[i]["id"], "units": body["items"][0]["units"]}
            ]
            response = api_client.post(url, data=body, format="json", headers=headers)
            orders.append(response)
        return orders

    return create_more_orders
