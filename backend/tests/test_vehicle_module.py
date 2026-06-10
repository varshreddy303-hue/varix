import calendar
import uuid
from datetime import date, datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app import models
from app.services.vehicle_service import _find_vehicle_document_conflict

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


def test_vehicle_unique_constraint_in_model():
    table = models.Vehicle.__table__
    uq_names = {constraint.name for constraint in table.constraints if getattr(constraint, "name", None)}
    assert "uq_vehicle_org_number" in uq_names


def test_full_vehicle_crud_and_tenant_isolation():
    org_a_name = f"test-org-a-{uuid.uuid4()}"
    org_b_name = f"test-org-b-{uuid.uuid4()}"
    org_a, token_a = create_org_and_admin(org_a_name, "admin_a@example.com", "SecurePass123")
    org_b, token_b = create_org_and_admin(org_b_name, "admin_b@example.com", "SecurePass123")

    vehicle_data = {
        "vehicle_number": "ABC-1234",
        "vehicle_type": "bus",
        "make": "Volvo",
        "model": "9700",
        "seating_capacity": 45,
        "fuel_type": "diesel",
        "registration_date": datetime.utcnow().isoformat(),
        "insurance_expiry_date": (datetime.utcnow() + timedelta(days=90)).isoformat(),
        "permit_expiry_date": (datetime.utcnow() + timedelta(days=120)).isoformat(),
        "fc_expiry_date": (datetime.utcnow() + timedelta(days=150)).isoformat(),
        "pollution_expiry_date": (datetime.utcnow() + timedelta(days=180)).isoformat(),
        "road_tax_expiry_date": (datetime.utcnow() + timedelta(days=210)).isoformat(),
        "purchase_price": 2500000.00,
        "emi_amount": 45000.00,
        "emi_due_day": 15,
    }

    create_resp = client.post(
        "/vehicles/",
        json=vehicle_data,
        headers=auth_headers(token_a, org_a["id"]),
    )
    assert create_resp.status_code == 201
    created_vehicle = create_resp.json()
    assert created_vehicle["vehicle_number"] == "ABC-1234"
    assert created_vehicle["organization_id"] == org_a["id"]

    get_resp = client.get(
        f"/vehicles/{created_vehicle['id']}",
        headers=auth_headers(token_a, org_a["id"]),
    )
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == created_vehicle["id"]

    list_resp = client.get(
        "/vehicles/",
        params={"vehicle_number": "ABC"},
        headers=auth_headers(token_a, org_a["id"]),
    )
    assert list_resp.status_code == 200
    assert any(item["id"] == created_vehicle["id"] for item in list_resp.json())

    update_resp = client.put(
        f"/vehicles/{created_vehicle['id']}",
        json={"make": "Mercedes", "vehicle_number": "ABC-1234"},
        headers=auth_headers(token_a, org_a["id"]),
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["make"] == "Mercedes"

    # tenant isolation: org B cannot access org A vehicle
    forbidden_resp = client.get(
        f"/vehicles/{created_vehicle['id']}",
        headers=auth_headers(token_b, org_b["id"]),
    )
    assert forbidden_resp.status_code == 404

    delete_resp = client.delete(
        f"/vehicles/{created_vehicle['id']}",
        headers=auth_headers(token_a, org_a["id"]),
    )
    assert delete_resp.status_code == 204

    get_deleted_resp = client.get(
        f"/vehicles/{created_vehicle['id']}",
        headers=auth_headers(token_a, org_a["id"]),
    )
    assert get_deleted_resp.status_code == 404


def test_expiring_documents_endpoint_returns_near_term_vehicles():
    org_name = f"test-org-expiry-{uuid.uuid4()}"
    org, token = create_org_and_admin(org_name, "expiry_admin@example.com", "SecurePass123")

    create_resp = client.post(
        "/vehicles/",
        json={
            "vehicle_number": "EXP-1234",
            "vehicle_type": "truck",
            "make": "Tata",
            "model": "Signa",
            "insurance_expiry_date": (datetime.utcnow() + timedelta(days=5)).isoformat(),
            "permit_expiry_date": (datetime.utcnow() + timedelta(days=60)).isoformat(),
            "purchase_price": 1800000.00,
        },
        headers=auth_headers(token, org["id"]),
    )
    assert create_resp.status_code == 201

    response = client.get(
        "/vehicles/expiring-documents",
        params={"within_days": 10},
        headers=auth_headers(token, org["id"]),
    )
    assert response.status_code == 200
    vehicles = response.json()
    assert any(vehicle["vehicle_number"] == "EXP-1234" for vehicle in vehicles)


@pytest.mark.parametrize(
    ("doc_field", "expiry_value"),
    [
        ("insurance_expiry_date", date(2026, 6, 12)),
        ("fc_expiry_date", date(2026, 6, 13)),
        ("permit_expiry_date", date(2026, 6, 14)),
        ("pollution_expiry_date", date(2026, 6, 15)),
        ("road_tax_expiry_date", date(2026, 6, 16)),
    ],
)
@pytest.mark.parametrize(
    "start_tz",
    [
        None,
        timezone.utc,
        timezone(timedelta(hours=5, minutes=30)),
    ],
)
def test_find_vehicle_document_conflict_normalizes_dates(doc_field, expiry_value, start_tz):
    vehicle = SimpleNamespace(
        insurance_expiry_date=None,
        permit_expiry_date=None,
        fc_expiry_date=None,
        pollution_expiry_date=None,
        road_tax_expiry_date=None,
        gps_subscription_expiry_date=None,
    )
    setattr(vehicle, doc_field, expiry_value)

    start = datetime(2026, 6, 10, 9, 0, tzinfo=start_tz)
    end = datetime(2026, 6, 20, 18, 0, tzinfo=start_tz)

    reason = _find_vehicle_document_conflict(vehicle, start, end)

    expected_labels = {
        "insurance_expiry_date": "insurance",
        "fc_expiry_date": "fitness certificate",
        "permit_expiry_date": "permit",
        "pollution_expiry_date": "pollution",
        "road_tax_expiry_date": "road tax",
    }

    assert reason is not None
    assert expected_labels[doc_field] in reason.lower()


def test_find_vehicle_document_conflict_handles_naive_and_aware_mixed_inputs():
    vehicle = SimpleNamespace(
        insurance_expiry_date=datetime(2026, 6, 12, 12, 0),
        permit_expiry_date=None,
        fc_expiry_date=None,
        pollution_expiry_date=None,
        road_tax_expiry_date=None,
        gps_subscription_expiry_date=None,
    )

    start = datetime(2026, 6, 10, 9, 0)
    end = datetime(2026, 6, 20, 18, 0, tzinfo=timezone.utc)

    reason = _find_vehicle_document_conflict(vehicle, start, end)

    assert reason is not None
    assert "insurance" in reason.lower()


def test_upcoming_emi_endpoint_calculates_next_due_date():
    org_name = f"test-org-emi-{uuid.uuid4()}"
    org, token = create_org_and_admin(org_name, "emi_admin@example.com", "SecurePass123")

    today = datetime.utcnow().date()
    due_day = today.day if today.day < 28 else 1
    expected_window_days = 10

    create_resp = client.post(
        "/vehicles/",
        json={
            "vehicle_number": "EMI-9876",
            "vehicle_type": "van",
            "make": "Maruti",
            "model": "Eeco",
            "emi_amount": 15000.00,
            "emi_due_day": due_day,
            "purchase_price": 850000.00,
        },
        headers=auth_headers(token, org["id"]),
    )
    assert create_resp.status_code == 201

    response = client.get(
        "/vehicles/upcoming-emi",
        params={"within_days": expected_window_days},
        headers=auth_headers(token, org["id"]),
    )
    assert response.status_code == 200
    vehicles = response.json()
    assert any(vehicle["vehicle_number"] == "EMI-9876" for vehicle in vehicles)
