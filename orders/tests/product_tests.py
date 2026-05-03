import pytest
from django.urls import reverse

from orders.models import Product


@pytest.mark.django_db
def test_create_product_no_authenticated_fails(api_client):
    url = reverse("products")

    body = {"name": "Test1", "price": 99}

    response = api_client.post(url, data=body)

    assert response.status_code == 401


@pytest.mark.django_db
def test_create_product_no_data_fails(api_client, headers):
    url = reverse("products")

    response = api_client.post(url, headers=headers)
    assert response.status_code == 400
    response = response.json()
    assert response.get("price")[0] == "This field is required."
    assert response.get("name")[0] == "This field is required."


@pytest.mark.django_db
def test_create_product_authenticated_success(create_products):
    create_products = create_products(num=1)[0]

    assert create_products.status_code == 201

    product = Product.objects.all()
    assert len(product) == 1

    product = product.first()
    create_products = create_products.json()
    assert product.name == create_products["name"]
    assert product.price == create_products["price"]


@pytest.mark.django_db
def test_list_products_no_authenticated_fails(api_client):
    url = reverse("products")
    response = api_client.get(url)

    assert response.status_code == 401


@pytest.mark.django_db
def test_list_products_authenticated_success(api_client, create_products, headers):
    create_products = create_products(num=3)

    url = reverse("products")
    response = api_client.get(url, headers=headers)

    assert response.status_code == 200
    response = response.json()

    assert len(create_products) == len(response["results"])


@pytest.mark.django_db
def test_list_products_pagination_success(api_client, create_products, headers):
    create_products(num=5)

    params = {"page": 1, "page_size": 3}

    url = reverse("products")
    response = api_client.get(url, headers=headers, data=params)

    assert response.status_code == 200
    response = response.json()

    assert len(response["results"]) == 3
    assert response["previous"] is None
    assert response["next"] is not None

    params = {"page": 2, "page_size": 3}
    response = api_client.get(url, headers=headers, data=params)

    assert response.status_code == 200
    response = response.json()

    assert len(response["results"]) == 2
    assert response["previous"] is not None
    assert response["next"] is None


@pytest.mark.django_db
def test_get_invalid_product_fails(api_client, headers):
    url = reverse("product_detail", kwargs={"pk": 99})
    response = api_client.get(url, headers=headers)

    assert response.status_code == 404


@pytest.mark.django_db
def test_get_product_no_authenticated_fails(api_client, headers, create_products):
    product = create_products(num=1)[0].json()
    url = reverse("product_detail", kwargs={"pk": product["id"]})
    response = api_client.get(url)

    assert response.status_code == 401


@pytest.mark.django_db
def test_get_product_authenticated_success(api_client, headers, create_products):
    product = create_products(num=1)[0].json()
    url = reverse("product_detail", kwargs={"pk": product["id"]})
    response = api_client.get(url, headers=headers)

    assert response.status_code == 200
    response = response.json()

    assert response["id"] == product["id"]
    assert response["name"] == product["name"]
    assert response["price"] == product["price"]


@pytest.mark.django_db
def test_delete_product_user_fails(api_client, headers, create_products):
    product = create_products(num=1)[0].json()

    url = reverse("product_detail", kwargs={"pk": product["id"]})
    response = api_client.delete(url, headers=headers)

    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_invalid_product_fails(api_client, headers_admin):
    url = reverse("product_detail", kwargs={"pk": 99})
    response = api_client.delete(url, headers=headers_admin)

    assert response.status_code == 404


@pytest.mark.django_db
def test_delete_product_admin_success(api_client, headers_admin, create_products):
    product = create_products(num=1)[0].json()

    url = reverse("product_detail", kwargs={"pk": product["id"]})
    response = api_client.delete(url, headers=headers_admin)

    assert response.status_code == 204

    assert not Product.objects.filter(id=product["id"]).exists()
