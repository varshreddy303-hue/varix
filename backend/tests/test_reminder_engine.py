import uuid
from datetime import datetime, timedelta

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


def test_default_reminder_rules_are_available_for_new_organization():
    org_name = f"test-reminders-org-{uuid.uuid4()}"
    org, token = create_org_and_admin(org_name, "reminder_admin@example.com", "SecurePass123")

    response = client.get(
        "/reminders/rules",
        headers=auth_headers(token, org["id"]),
    )
    assert response.status_code == 200
    rules = response.json()
    assert len(rules) >= 1
    assert any(rule["event_type"] == "invoice_due" for rule in rules)


def test_generate_reminders_for_vehicle_expiry_and_emi_due():
    org_name = f"test-reminders-expiry-{uuid.uuid4()}"
    org, token = create_org_and_admin(org_name, "expiry_admin@example.com", "SecurePass123")

    create_resp = client.post(
        "/vehicles/",
        json={
            "vehicle_number": "REM-EXP-001",
            "vehicle_type": "bus",
            "make": "Volvo",
            "model": "B9R",
            "insurance_expiry_date": (datetime.utcnow() + timedelta(days=20)).isoformat(),
            "gps_subscription_expiry_date": (datetime.utcnow() + timedelta(days=20)).isoformat(),
            "service_due_date": (datetime.utcnow() + timedelta(days=5)).isoformat(),
            "battery_change_due_date": (datetime.utcnow() + timedelta(days=6)).isoformat(),
            "tyre_change_due_date": (datetime.utcnow() + timedelta(days=6)).isoformat(),
            "purchase_price": 3200000.00,
            "emi_amount": 50000.00,
            "emi_due_day": datetime.utcnow().day,
            "loan_closure_date": (datetime.utcnow() + timedelta(days=60)).isoformat(),
        },
        headers=auth_headers(token, org["id"]),
    )
    assert create_resp.status_code == 201

    generate_resp = client.post(
        "/reminders/generate",
        headers=auth_headers(token, org["id"]),
    )
    assert generate_resp.status_code == 200
    reminders = generate_resp.json()
    event_types = {reminder["message"] for reminder in reminders}
    assert any("Insurance expiry" in message or "reminder" in message.lower() for message in event_types)
    assert any(reminder["entity_type"] == "vehicle" for reminder in reminders)

    list_resp = client.get(
        "/reminders/",
        headers=auth_headers(token, org["id"]),
    )
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= len(reminders)


def test_notification_preference_upsert_and_list():
    org_name = f"test-reminders-pref-{uuid.uuid4()}"
    org, token = create_org_and_admin(org_name, "pref_admin@example.com", "SecurePass123")

    create_resp = client.post(
        "/reminders/notification-preferences",
        json={
            "event_type": "invoice_due",
            "channel": "email",
            "enabled": True,
        },
        headers=auth_headers(token, org["id"]),
    )
    assert create_resp.status_code == 201
    preference = create_resp.json()
    assert preference["event_type"] == "invoice_due"
    assert preference["channel"] == "email"

    list_resp = client.get(
        "/reminders/notification-preferences",
        headers=auth_headers(token, org["id"]),
    )
    assert list_resp.status_code == 200
    preferences = list_resp.json()
    assert any(pref["event_type"] == "invoice_due" and pref["channel"] == "email" for pref in preferences)
