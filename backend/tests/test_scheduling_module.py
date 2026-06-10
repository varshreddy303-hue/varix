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


def create_customer(token: str, org_id: str):
    response = client.post(
        "/customers/",
        json={
            "customer_name": "Maintenance Customer",
            "phone_number": "+911234567891",
            "email": "maintenance-customer@example.com",
        },
        headers=auth_headers(token, org_id),
    )
    assert response.status_code == 201
    return response.json()


def create_vehicle(token: str, org_id: str):
    response = client.post(
        "/vehicles/",
        json={
            "vehicle_number": "MNT-1234",
            "vehicle_type": "bus",
            "make": "Ashok Leyland",
            "model": "Tata",
            "seating_capacity": 20,
            "fuel_type": "diesel",
            "registration_date": datetime.utcnow().isoformat(),
            "purchase_price": 1200000.00,
        },
        headers=auth_headers(token, org_id),
    )
    assert response.status_code == 201
    return response.json()


def test_vehicle_availability_blocks_maintenance():
    org_name = f"schedule-org-{uuid.uuid4()}"
    org, token = create_org_and_admin(org_name, "schedule_admin@example.com", "SecurePass123")
    customer = create_customer(token, org["id"])
    vehicle = create_vehicle(token, org["id"])

    start = datetime.utcnow() + timedelta(days=1)
    end = start + timedelta(days=2)

    schedule_resp = client.post(
        "/maintenance/",
        json={
            "vehicle_id": vehicle["id"],
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "reason": "Engine service",
        },
        headers=auth_headers(token, org["id"]),
    )
    assert schedule_resp.status_code == 201

    availability_resp = client.get(
        "/vehicles/availability",
        params={
            "vehicle_id": vehicle["id"],
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
        },
        headers=auth_headers(token, org["id"]),
    )
    assert availability_resp.status_code == 200
    assert availability_resp.json()["available"] is False
    assert "maintenance" in availability_resp.json()["reason"].lower()


def test_create_maintenance_schedule_blocks_conflicting_booking():
    org_name = f"schedule-org-conflict-{uuid.uuid4()}"
    org, token = create_org_and_admin(org_name, "conflict_admin@example.com", "SecurePass123")
    customer = create_customer(token, org["id"])
    vehicle = create_vehicle(token, org["id"])

    start = datetime.utcnow() + timedelta(days=2)
    end = start + timedelta(days=3)

    booking_resp = client.post(
        "/bookings/",
        json={
            "customer_id": customer["id"],
            "vehicle_id": vehicle["id"],
            "pickup_location": "Depot A",
            "destination": "Depot B",
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "booking_amount": 8500.00,
        },
        headers=auth_headers(token, org["id"]),
    )
    assert booking_resp.status_code == 201

    schedule_resp = client.post(
        "/maintenance/",
        json={
            "vehicle_id": vehicle["id"],
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "reason": "Preventive maintenance",
        },
        headers=auth_headers(token, org["id"]),
    )
    assert schedule_resp.status_code == 409


def test_calendar_returns_booking_and_maintenance_events():
    org_name = f"schedule-org-calendar-{uuid.uuid4()}"
    org, token = create_org_and_admin(org_name, "calendar_admin@example.com", "SecurePass123")
    customer = create_customer(token, org["id"])
    vehicle = create_vehicle(token, org["id"])

    booking_start = datetime.utcnow() + timedelta(days=4)
    booking_end = booking_start + timedelta(days=1)
    booking_resp = client.post(
        "/bookings/",
        json={
            "customer_id": customer["id"],
            "vehicle_id": vehicle["id"],
            "pickup_location": "Depot A",
            "destination": "Depot C",
            "start_date": booking_start.isoformat(),
            "end_date": booking_end.isoformat(),
            "booking_amount": 9800.00,
        },
        headers=auth_headers(token, org["id"]),
    )
    assert booking_resp.status_code == 201

    maintenance_start = booking_end + timedelta(days=1)
    maintenance_end = maintenance_start + timedelta(days=1)
    maintenance_resp = client.post(
        "/maintenance/",
        json={
            "vehicle_id": vehicle["id"],
            "start_date": maintenance_start.isoformat(),
            "end_date": maintenance_end.isoformat(),
            "reason": "Oil change",
        },
        headers=auth_headers(token, org["id"]),
    )
    assert maintenance_resp.status_code == 201

    calendar_resp = client.get(
        "/calendar",
        params={
            "start_date": datetime.utcnow().isoformat(),
            "end_date": (maintenance_end + timedelta(days=1)).isoformat(),
        },
        headers=auth_headers(token, org["id"]),
    )
    assert calendar_resp.status_code == 200
    events = calendar_resp.json()
    assert any(event["event_type"] == "booking" for event in events)
    assert any(event["event_type"] == "maintenance" for event in events)
