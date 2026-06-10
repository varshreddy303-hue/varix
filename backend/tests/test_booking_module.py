import uuid
from datetime import datetime, timedelta

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


def create_customer(token: str, org_id: str):
    response = client.post(
        "/customers/",
        json={
            "customer_name": "Test Customer",
            "phone_number": "+911234567890",
            "email": "customer@example.com",
        },
        headers=auth_headers(token, org_id),
    )
    assert response.status_code == 201
    return response.json()


def create_vehicle(token: str, org_id: str):
    response = client.post(
        "/vehicles/",
        json={
            "vehicle_number": "TST-1234",
            "vehicle_type": "van",
            "make": "Tata",
            "model": "Ace",
            "seating_capacity": 6,
            "fuel_type": "diesel",
            "registration_date": datetime.utcnow().isoformat(),
            "purchase_price": 800000.00,
        },
        headers=auth_headers(token, org_id),
    )
    assert response.status_code == 201
    return response.json()


def test_booking_model_has_status_and_course_fields():
    table = models.Booking.__table__
    columns = {col.name for col in table.columns}
    assert "status" in columns
    assert "pickup_location" in columns
    assert "destination" in columns
    assert "start_date" in columns
    assert "end_date" in columns
    assert "booking_amount" in columns


def test_create_booking_and_prevent_double_booking():
    org_name = f"booking-org-{uuid.uuid4()}"
    org, token = create_org_and_admin(org_name, "booking_admin@example.com", "SecurePass123")
    customer = create_customer(token, org["id"])
    vehicle = create_vehicle(token, org["id"])

    start = datetime.utcnow()
    end = start + timedelta(days=3)

    create_resp = client.post(
        "/bookings/",
        json={
            "customer_id": customer["id"],
            "vehicle_id": vehicle["id"],
            "pickup_location": "Depot A",
            "destination": "Depot B",
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "booking_amount": 12000.00,
        },
        headers=auth_headers(token, org["id"]),
    )
    assert create_resp.status_code == 201
    booking = create_resp.json()
    assert booking["status"] == "pending"

    conflict_resp = client.post(
        "/bookings/",
        json={
            "customer_id": customer["id"],
            "vehicle_id": vehicle["id"],
            "pickup_location": "Depot C",
            "destination": "Depot D",
            "start_date": (start + timedelta(days=1)).isoformat(),
            "end_date": (end + timedelta(days=1)).isoformat(),
            "booking_amount": 10000.00,
        },
        headers=auth_headers(token, org["id"]),
    )
    assert conflict_resp.status_code == 409


def test_cancelled_booking_does_not_block_availability():
    org_name = f"booking-org-cancel-{uuid.uuid4()}"
    org, token = create_org_and_admin(org_name, "cancel_admin@example.com", "SecurePass123")
    customer = create_customer(token, org["id"])
    vehicle = create_vehicle(token, org["id"])

    start = datetime.utcnow()
    end = start + timedelta(days=2)

    booking_resp = client.post(
        "/bookings/",
        json={
            "customer_id": customer["id"],
            "vehicle_id": vehicle["id"],
            "pickup_location": "Depot A",
            "destination": "Depot B",
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "booking_amount": 9000.00,
        },
        headers=auth_headers(token, org["id"]),
    )
    assert booking_resp.status_code == 201
    booking = booking_resp.json()

    cancel_resp = client.post(
        f"/bookings/{booking['id']}/cancel",
        headers=auth_headers(token, org["id"]),
    )
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "cancelled"

    availability_resp = client.get(
        "/bookings/availability",
        params={
            "vehicle_id": vehicle["id"],
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
        },
        headers=auth_headers(token, org["id"]),
    )
    assert availability_resp.status_code == 200
    assert availability_resp.json()["available"] is True


def test_tenant_isolation_for_bookings():
    org_a_name = f"booking-org-a-{uuid.uuid4()}"
    org_b_name = f"booking-org-b-{uuid.uuid4()}"
    org_a, token_a = create_org_and_admin(org_a_name, "booking_a_admin@example.com", "SecurePass123")
    org_b, token_b = create_org_and_admin(org_b_name, "booking_b_admin@example.com", "SecurePass123")

    customer_a = create_customer(token_a, org_a["id"])
    vehicle_a = create_vehicle(token_a, org_a["id"])

    start = datetime.utcnow()
    end = start + timedelta(days=1)

    create_resp = client.post(
        "/bookings/",
        json={
            "customer_id": customer_a["id"],
            "vehicle_id": vehicle_a["id"],
            "pickup_location": "Depot A",
            "destination": "Depot B",
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "booking_amount": 7000.00,
        },
        headers=auth_headers(token_a, org_a["id"]),
    )
    assert create_resp.status_code == 201
    booking = create_resp.json()

    forbidden_resp = client.get(
        f"/bookings/{booking['id']}",
        headers=auth_headers(token_b, org_b["id"]),
    )
    assert forbidden_resp.status_code == 404
