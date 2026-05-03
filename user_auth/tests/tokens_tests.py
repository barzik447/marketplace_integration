import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_get_access_token_invalid_user_fails(api_client):

    url = reverse("access_token")
    data = {"username": "invalid_user", "password": "invalid_password"}
    response = api_client.post(url, data)

    assert response.status_code == 401


@pytest.mark.django_db
def test_get_access_token_valid_user_success(api_client, access_refresh_tokens):

    response = access_refresh_tokens
    assert response.status_code == 200

    response = response.json()
    assert response.get("access") is not None
    assert response.get("refresh") is not None


@pytest.mark.django_db
def test_refresh_access_token_success(api_client, access_refresh_tokens):
    access_refresh_tokens = access_refresh_tokens.json()
    refresh_token = access_refresh_tokens.get("refresh")

    url = reverse("refresh")

    data = {"refresh": refresh_token}
    response = api_client.post(url, data=data)

    assert response.status_code == 200

    response = response.json()
    assert response.get("access") is not None


@pytest.mark.django_db
def test_refresh_access_token_invalid_refresh_token_fails(api_client):
    url = reverse("refresh")

    data = {"refresh": "invalid_token"}
    response = api_client.post(url, data=data)

    assert response.status_code == 401
