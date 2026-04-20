import pytest
from leads.models import Lead


# ---------------- CREATE ---------------- #

@pytest.mark.django_db
def test_create_lead_success(client, auth_token):
    response = client.post(
        "/api/leads/",
        {
            "name": "John",
            "company": "Google",
            "email": "john1@gmail.com"
        },
        HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        HTTP_IDEMPOTENCY_KEY="unique-key-123"
    )

    assert response.status_code == 201


@pytest.mark.django_db
def test_create_lead_without_auth(client):
    response = client.post(
        "/api/leads/",
        {
            "name": "John",
            "company": "Google",
            "email": "john2@gmail.com"
        }
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_missing_idempotency_key(client, auth_token):
    response = client.post(
        "/api/leads/",
        {
            "name": "John",
            "company": "Google",
            "email": "john3@gmail.com"
        },
        HTTP_AUTHORIZATION=f"Bearer {auth_token}"
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_idempotency(client, auth_token):
    data = {
        "name": "John",
        "company": "Google",
        "email": "john4@gmail.com"
    }

    headers = {
        "HTTP_AUTHORIZATION": f"Bearer {auth_token}",
        "HTTP_IDEMPOTENCY_KEY": "same-key"
    }

    r1 = client.post("/api/leads/", data, **headers)
    r2 = client.post("/api/leads/", data, **headers)

    assert r1.data["id"] == r2.data["id"]
    assert Lead.objects.count() == 1


@pytest.mark.django_db
def test_duplicate_email(client, auth_token):
    Lead.objects.create(
        name="John",
        company="Google",
        email="dup@gmail.com"
    )

    response = client.post(
        "/api/leads/",
        {
            "name": "John",
            "company": "Google",
            "email": "dup@gmail.com"
        },
        HTTP_AUTHORIZATION=f"Bearer {auth_token}",
        HTTP_IDEMPOTENCY_KEY="new-key"
    )

    assert response.status_code == 400


# ---------------- DETAIL ---------------- #

@pytest.mark.django_db
def test_get_lead_detail(client, auth_token):
    lead = Lead.objects.create(
        name="Alice",
        company="Amazon",
        email="alice@gmail.com"
    )

    response = client.get(
        f"/api/leads/{lead.id}/",
        HTTP_AUTHORIZATION=f"Bearer {auth_token}"
    )

    assert response.status_code == 200


@pytest.mark.django_db
def test_get_lead_detail_unauthorized(client):
    lead = Lead.objects.create(
        name="Bob",
        company="Meta",
        email="bob@gmail.com"
    )

    response = client.get(f"/api/leads/{lead.id}/")

    assert response.status_code == 401


# ---------------- LIST ---------------- #

@pytest.mark.django_db
def test_get_all_leads(client):
    Lead.objects.create(name="A", company="X", email="a@gmail.com")
    Lead.objects.create(name="B", company="Y", email="b@gmail.com")

    response = client.get("/api/leads/all/")

    assert response.status_code == 200
    assert len(response.data) == 2