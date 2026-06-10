import uuid
from datetime import datetime

from fastapi.testclient import TestClient

from app.main import app
from app import models

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


def test_package_model_fields_present():
    columns = {col.name for col in models.TripPackage.__table__.columns}
    assert "name" in columns
    assert "package_category" in columns
    assert "included_hours" in columns
    assert "included_km" in columns
    assert "base_amount" in columns
    assert "extra_km_rate" in columns
    assert "extra_hour_rate" in columns
    assert "driver_bata_default" in columns
    assert "night_charge_default" in columns
    assert "permit_default" in columns
    assert "state_tax_default" in columns
    assert "minimum_km_per_day" in columns
    assert "km_rate" in columns
    assert "active" in columns


def test_create_read_update_delete_package_flow():
    org_name = f"package-org-{uuid.uuid4()}"
    org, token = create_org_and_admin(org_name, "package_admin@example.com", "SecurePass123")

    create_resp = client.post(
        "/trip-packages/",
        json={
            "name": "Local 8hr/80km",
            "package_category": "Local",
            "included_hours": 8,
            "included_km": 80,
            "base_amount": 4200.00,
            "extra_km_rate": 45.0,
            "extra_hour_rate": 400.0,
            "driver_bata_default": 500.0,
            "night_charge_default": 600.0,
            "permit_default": 200.0,
            "state_tax_default": 150.0,
            "minimum_km_per_day": 80,
            "km_rate": 60.0,
            "active": True,
        },
        headers=auth_headers(token, org["id"]),
    )
    assert create_resp.status_code == 201
    package = create_resp.json()
    assert package["name"] == "Local 8hr/80km"
    assert package["package_category"] == "Local"
    assert package["active"] is True

    get_resp = client.get(f"/trip-packages/{package['id']}", headers=auth_headers(token, org["id"]))
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Local 8hr/80km"

    update_resp = client.put(
        f"/trip-packages/{package['id']}",
        json={"base_amount": 4500.0, "active": False},
        headers=auth_headers(token, org["id"]),
    )
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["base_amount"] == 4500.0
    assert updated["active"] is False

    delete_resp = client.delete(f"/trip-packages/{package['id']}", headers=auth_headers(token, org["id"]))
    assert delete_resp.status_code == 204

    missing_resp = client.get(f"/trip-packages/{package['id']}", headers=auth_headers(token, org["id"]))
    assert missing_resp.status_code == 404


def test_package_list_and_tenant_isolation():
    org_a_name = f"package-org-a-{uuid.uuid4()}"
    org_b_name = f"package-org-b-{uuid.uuid4()}"
    org_a, token_a = create_org_and_admin(org_a_name, "package_a_admin@example.com", "SecurePass123")
    org_b, token_b = create_org_and_admin(org_b_name, "package_b_admin@example.com", "SecurePass123")

    first_resp = client.post(
        "/trip-packages/",
        json={
            "name": "300 KM Average",
            "package_category": "Local",
            "included_km": 300,
            "base_amount": 10500.0,
            "active": True,
        },
        headers=auth_headers(token_a, org_a["id"]),
    )
    assert first_resp.status_code == 201

    second_resp = client.post(
        "/trip-packages/",
        json={
            "name": "Outstation Standard",
            "package_category": "Outstation",
            "base_amount": 15000.0,
            "active": True,
        },
        headers=auth_headers(token_b, org_b["id"]),
    )
    assert second_resp.status_code == 201

    list_a = client.get("/trip-packages/", headers=auth_headers(token_a, org_a["id"]))
    assert list_a.status_code == 200
    assert any(item["name"] == "300 KM Average" for item in list_a.json())
    assert all(item["name"] != "Outstation Standard" for item in list_a.json())

    list_b = client.get("/trip-packages/", headers=auth_headers(token_b, org_b["id"]))
    assert list_b.status_code == 200
    assert any(item["name"] == "Outstation Standard" for item in list_b.json())
    assert all(item["name"] != "300 KM Average" for item in list_b.json())
