import uuid
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create_org_and_admin(name: str, email: str, password: str):
    org_resp = client.post(
        "/auth/organizations/register",
        json={"name": name, "admin_email": email, "admin_password": password},
    )
    assert org_resp.status_code == 201
    org = org_resp.json()

    login_resp = client.post(
        "/auth/login",
        json={"organization_id": org["id"], "email": email, "password": password},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    return org, token


def auth_headers(token: str, organization_id: str):
    return {
        "Authorization": f"Bearer {token}",
        "X-Organization-Id": organization_id,
    }


def test_create_customer_with_only_phone_number():
    org_name = f"test-customer-phone-{uuid.uuid4()}"
    org, token = create_org_and_admin(org_name, "customer_phone_admin@example.com", "SecurePass123")

    response = client.post(
        "/customers/",
        json={
            "phone_number": "+911234567890",
        },
        headers=auth_headers(token, org["id"]),
    )

    assert response.status_code == 201
    customer = response.json()
    assert customer["phone_number"] == "+911234567890"
    assert customer["customer_name"] == ""
    assert customer["organization_id"] == org["id"]


def test_create_customer_with_only_name():
    org_name = f"test-customer-name-{uuid.uuid4()}"
    org, token = create_org_and_admin(org_name, "customer_name_admin@example.com", "SecurePass123")

    response = client.post(
        "/customers/",
        json={
            "customer_name": "Minimal Customer",
        },
        headers=auth_headers(token, org["id"]),
    )

    assert response.status_code == 201
    customer = response.json()
    assert customer["customer_name"] == "Minimal Customer"
    assert customer["phone_number"] == ""
    assert customer["organization_id"] == org["id"]


def test_create_customer_requires_name_or_phone():
    org_name = f"test-customer-validation-{uuid.uuid4()}"
    org, token = create_org_and_admin(org_name, "customer_validation_admin@example.com", "SecurePass123")

    response = client.post(
        "/customers/",
        json={
            "email": "info@example.com",
        },
        headers=auth_headers(token, org["id"]),
    )

    assert response.status_code == 422
    assert response.json()["detail"]
