from unittest.mock import patch

import pytest
from django.urls import reverse

from orders.models import Order


@pytest.mark.django_db
def test_create_order_unauthenticated_fails(api_client):
    url = reverse("orders")
    response = api_client.post(url, data={})
    assert response.status_code == 401


@pytest.mark.django_db
def test_create_order_no_data_fails(api_client, headers):
    url = reverse("orders")
    response = api_client.post(url, headers=headers)
    assert response.status_code == 400
    data = response.json()
    assert "items" in data


@pytest.mark.django_db
def test_create_order_invalid_units_fails(api_client, headers, create_products):
    product = create_products(num=1)[0].json()
    url = reverse("orders")
    body = {
        "description": "Bad units",
        "items": [{"product": product["id"], "units": 0}],
    }
    response = api_client.post(url, data=body, format="json", headers=headers)
    assert response.status_code == 400


@pytest.mark.django_db
def test_create_order_price_is_calculated(api_client, headers, create_products):
    product = create_products(num=1)[0].json()
    url = reverse("orders")
    body = {
        "description": "Price check",
        "items": [{"product": product["id"], "units": 3}],
        "price": 999999,
    }
    response = api_client.post(url, data=body, format="json", headers=headers)
    assert response.status_code == 201
    response = response.json()

    assert response["price"] == product["price"] * 3


@pytest.mark.django_db
def test_create_order_creates_two_marketplaces(api_client, headers, create_products):
    product = create_products(num=1)[0].json()
    url = reverse("orders")
    body = {
        "description": "Marketplaces check",
        "items": [{"product": product["id"], "units": 1}],
    }
    response = api_client.post(url, data=body, format="json", headers=headers)
    assert response.status_code == 201
    response = response.json()

    order = Order.objects.get(id=response["id"])
    names = set(order.marketplaces.values_list("marketplace_name", flat=True))
    assert names == {"AmazonFake", "AliexpressFake"}


@pytest.mark.django_db
def test_create_order_marketplaces_initial_status_pending(
    api_client, headers, create_products
):
    product = create_products(num=1)[0].json()
    url = reverse("orders")
    body = {
        "description": "Status check",
        "items": [{"product": product["id"], "units": 1}],
    }
    response = api_client.post(url, data=body, format="json", headers=headers)
    assert response.status_code == 201

    order = Order.objects.get(id=response.json()["id"])
    for marketplace in order.marketplaces.all():
        assert marketplace.status == 0


@pytest.mark.django_db(transaction=True)
def test_create_order_celery_delay_called_once_per_marketplace(
    api_client, headers, create_products
):
    product = create_products(num=1)[0].json()
    url = reverse("orders")
    body = {
        "description": "Celery trigger",
        "items": [{"product": product["id"], "units": 1}],
    }

    with patch("orders.views.send_order_marketplace.delay") as mock_delay:
        response = api_client.post(url, data=body, format="json", headers=headers)

    assert response.status_code == 201
    assert mock_delay.call_count == 2
    response = response.json()

    order = Order.objects.get(id=response["id"])
    expected_ids = set(order.marketplaces.values_list("id", flat=True))
    called_ids = {c.args[0] for c in mock_delay.call_args_list}
    assert called_ids == expected_ids


@pytest.mark.django_db(transaction=True)
def test_create_order_celery_not_called_on_bad_request(api_client, headers):
    url = reverse("orders")
    body = {"description": "Missing items"}

    with patch("orders.views.send_order_marketplace.delay") as mock_delay:
        response = api_client.post(url, data=body, headers=headers)

    assert response.status_code == 400
    mock_delay.assert_not_called()


@pytest.mark.django_db
def test_list_orders_unauthenticated_fails(api_client):
    url = reverse("orders")
    response = api_client.get(url)
    assert response.status_code == 401


@pytest.mark.django_db
def test_list_orders_user_sees_only_own_orders(api_client, headers, create_orders):
    create_orders(num=2)
    url = reverse("orders")
    response = api_client.get(url, headers=headers)
    assert response.status_code == 200
    response = response.json()

    assert len(response["results"]) == 2


@pytest.mark.django_db
def test_list_orders_admin_sees_all_orders(
    api_client, headers, headers_admin, create_orders, create_products
):
    create_orders(num=2)

    product = create_products(num=1)[0].json()
    api_client.post(
        reverse("orders"),
        data={
            "description": "Admin order",
            "items": [{"product": product["id"], "units": 1}],
        },
        format="json",
        headers=headers_admin,
    )

    url = reverse("orders")
    response_user = api_client.get(url, headers=headers)
    response_user = response_user.json()
    assert len(response_user["results"]) == 2

    response_admin = api_client.get(url, headers=headers_admin)
    response_admin = response_admin.json()

    assert len(response_admin["results"]) == 3


@pytest.mark.django_db
def test_list_orders_pagination(api_client, headers, create_orders):
    create_orders(num=5)
    url = reverse("orders")

    response = api_client.get(url, headers=headers, data={"page": 1, "page_size": 3})
    assert response.status_code == 200
    response = response.json()

    assert len(response["results"]) == 3
    assert response["previous"] is None
    assert response["next"] is not None

    response = api_client.get(url, headers=headers, data={"page": 2, "page_size": 3})
    assert response.status_code == 200
    response = response.json()

    assert len(response["results"]) == 2
    assert response["previous"] is not None
    assert response["next"] is None


@pytest.mark.django_db
def test_get_order_unauthenticated_fails(api_client, create_orders):
    order = create_orders(num=1)[0].json()
    url = reverse("order_detail", kwargs={"pk": order["id"]})
    response = api_client.get(url)
    assert response.status_code == 401


@pytest.mark.django_db
def test_get_order_invalid_pk_fails(api_client, headers):
    url = reverse("order_detail", kwargs={"pk": 99999})
    response = api_client.get(url, headers=headers)
    assert response.status_code == 404


@pytest.mark.django_db
def test_get_order_creator_success(api_client, headers, create_orders):
    order = create_orders(num=1)[0].json()
    url = reverse("order_detail", kwargs={"pk": order["id"]})
    response = api_client.get(url, headers=headers)

    assert response.status_code == 200
    response = response.json()

    assert response["id"] == order["id"]
    assert response["description"] == order["description"]
    assert response["price"] == order["price"]
    assert "marketplaces" in response
    assert "items" in response


@pytest.mark.django_db
def test_get_order_admin_can_read_any_order(api_client, headers_admin, create_orders):
    order = create_orders(num=1)[0].json()
    url = reverse("order_detail", kwargs={"pk": order["id"]})
    response = api_client.get(url, headers=headers_admin)
    assert response.status_code == 200


@pytest.mark.django_db
def test_update_order_unauthenticated_fails(api_client, create_orders):
    order = create_orders(num=1)[0].json()
    url = reverse("order_detail", kwargs={"pk": order["id"]})
    response = api_client.patch(url, data={"description": "Hack"})
    assert response.status_code == 401


@pytest.mark.django_db
def test_update_order_creator_success(api_client, headers, create_orders):
    order = create_orders(num=1)[0].json()
    url = reverse("order_detail", kwargs={"pk": order["id"]})
    response = api_client.patch(
        url,
        data={"description": "Updated"},
        headers=headers,
    )
    assert response.status_code == 200
    response = response.json()

    assert response["description"] == "Updated"


@pytest.mark.django_db
def test_update_order_admin_success(api_client, headers_admin, create_orders):
    order = create_orders(num=1)[0].json()
    url = reverse("order_detail", kwargs={"pk": order["id"]})
    response = api_client.patch(
        url,
        data={"description": "Admin edit"},
        headers=headers_admin,
    )
    assert response.status_code == 200
    response = response.json()

    assert response["description"] == "Admin edit"
