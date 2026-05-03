import pytest
from django.urls import reverse

from django.contrib.auth.models import User


@pytest.mark.django_db
def test_register_no_data_fails(api_client):
    url = reverse("register")

    data = {}
    response = api_client.post(url, data)

    assert response.status_code == 400


@pytest.mark.django_db
def test_register_valid_data_success(api_client, register_user_test):
    response = register_user_test["response"]
    data = register_user_test["data"]
    assert response.status_code == 201

    response = response.json()
    new_user = User.objects.filter(id=response["id"])
    assert len(new_user) == 1

    new_user = new_user.first()
    assert new_user.username == data["username"]


@pytest.mark.django_db
def test_register_different_password_fails(api_client):
    url = reverse("register")

    data = {
        "username": "test",
        "password": "test",
        "password2": "different",
    }
    response = api_client.post(url, data)

    assert response.status_code == 400
    assert "Passwords didn't match" in response.text
