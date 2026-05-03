import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def register_user_test(api_client):
    url = reverse("register")
    data = {"username": "test", "password": "test", "password2": "test"}

    return {
        "response": api_client.post(url, data),
        "data": data,
    }


@pytest.fixture
def access_refresh_tokens(api_client, register_user_test):
    url = reverse("access_token")
    user_data = register_user_test["data"]
    data = {"username": user_data["username"], "password": user_data["password"]}

    return api_client.post(url, data)


@pytest.fixture
def headers(access_refresh_tokens):
    return {"Authorization": f"Bearer {access_refresh_tokens.json()['access']}"}


@pytest.fixture
def access_refresh_tokens_admin(api_client):

    User.objects.create_superuser("admin", "admin@gmail.com", "admin")

    url = reverse("access_token")
    data = {"username": "admin", "password": "admin"}

    return api_client.post(url, data)


@pytest.fixture
def headers_admin(access_refresh_tokens_admin):
    return {"Authorization": f"Bearer {access_refresh_tokens_admin.json()['access']}"}
