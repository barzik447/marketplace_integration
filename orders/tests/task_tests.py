from unittest.mock import Mock, patch

import pytest

from orders.exceptions import ApiStatusException
from orders.models import Order
from orders.tasks import (
    aliexpress_fake_data,
    amazon_fake_data,
    send_order_marketplace,
)


@pytest.mark.django_db
def test_amazon_fake_data(create_orders):
    order = create_orders(num=1)[0]
    order = Order.objects.get(id=order.json()["id"])
    marketplace = order.marketplaces.get(marketplace_name="AmazonFake")
    products = order.order_items.select_related("product").all()
    data = amazon_fake_data(marketplace, products)
    expected_data = {
        "userId": order.creator.id,
        "products": [
            {
                "id": products[0].product.id,
                "price": products[0].product.price,
            }
        ],
    }
    assert data == expected_data


@pytest.mark.django_db
def test_aliexpress_fake_data(create_orders):
    order = create_orders(num=1)[0]
    order = Order.objects.get(id=order.json()["id"])
    marketplace = order.marketplaces.get(marketplace_name="AliexpressFake")
    products = order.order_items.select_related("product").all()
    data = aliexpress_fake_data(marketplace, products)

    expected_data = {
        "user_id": order.creator.id,
        "items": [
            {
                "product_id": products[0].product.id,
                "quantity": products[0].units,
            }
        ],
    }
    assert data == expected_data


@pytest.mark.django_db
@patch("orders.tasks.httpx.post")
def test_send_order_marketplace_success(mock_post, create_orders):
    mock_post.return_value = Mock(status_code=201)
    order = create_orders(num=1)[0].json()
    order = Order.objects.get(id=order["id"])
    marketplace = order.marketplaces.get(marketplace_name="AmazonFake")
    send_order_marketplace.apply(args=[marketplace.id])
    marketplace.refresh_from_db()

    assert marketplace.status == 1
    assert marketplace.date_success is not None
    assert marketplace.date_error is None


@pytest.mark.django_db
@patch("orders.tasks.httpx.post")
def test_send_order_marketplace_calls_httpx_with_correct_data(mock_post, create_orders):
    mock_post.return_value = Mock(status_code=201)
    order = create_orders(num=1)[0].json()
    order = Order.objects.get(id=order["id"])
    marketplace = order.marketplaces.get(marketplace_name="AmazonFake")
    send_order_marketplace.apply(args=[marketplace.id])
    product = order.order_items.first()

    expected_data = {
        "userId": order.creator.id,
        "products": [
            {
                "id": product.product.id,
                "price": product.product.price,
            }
        ],
    }

    mock_post.assert_called_once_with(marketplace.url_marketplace, json=expected_data)


@pytest.mark.django_db
@patch("orders.tasks.httpx.post")
def test_send_order_marketplace_sets_error_status_on_400(mock_post, create_orders):
    mock_post.return_value = Mock(status_code=400, text="Bad request")
    order = create_orders(num=1)[0].json()
    order = Order.objects.get(id=order["id"])
    marketplace = order.marketplaces.get(marketplace_name="AmazonFake")
    send_order_marketplace.apply(args=[marketplace.id])
    marketplace.refresh_from_db()

    assert marketplace.status == 2
    assert marketplace.date_error is not None
    assert marketplace.api_call_error_msg == "Bad request"


@pytest.mark.django_db
@patch("orders.tasks.httpx.post")
def test_send_order_marketplace_retries_on_500(mock_post, create_orders):
    mock_post.return_value = Mock(status_code=500)
    order = create_orders(num=1)[0].json()
    order = Order.objects.get(id=order["id"])
    marketplace = order.marketplaces.get(marketplace_name="AmazonFake")

    with pytest.raises(ApiStatusException):
        send_order_marketplace.run(marketplace.id)


@pytest.mark.django_db
@patch("orders.tasks.httpx.post")
def test_send_order_marketplace_retries_on_429(mock_post, create_orders):
    mock_post.return_value = Mock(status_code=429)
    order = create_orders(num=1)[0].json()
    order = Order.objects.get(id=order["id"])
    marketplace = order.marketplaces.get(marketplace_name="AmazonFake")

    with pytest.raises(ApiStatusException):
        send_order_marketplace.run(marketplace.id)
