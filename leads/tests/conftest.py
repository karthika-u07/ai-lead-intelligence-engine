import pytest
from unittest.mock import patch
from django.contrib.auth.models import User
from rest_framework.test import APIClient


@pytest.fixture(autouse=True)
def mock_celery():
    with patch("leads.views.enrich_lead_task.delay"):
        yield


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def auth_token(client):
    user = User.objects.create_user(
        username="testuser",
        password="testpass"
    )

    response = client.post("/api/token/", {
        "username": "testuser",
        "password": "testpass"
    })

    return response.data["access"]