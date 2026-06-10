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
            "customer_name": "Expense Customer",
            "phone_number": "+911234567891",
            "email": "expense_customer@example.com",
        },
        headers=auth_headers(token, org_id),
    )
    assert response.status_code == 201
    return response.json()


def create_vehicle(token: str, org_id: str):
    response = client.post(
        "/vehicles/",
        json={
            "vehicle_number": "EXP-001",
            "vehicle_type": "truck",
            "make": "Mahindra",
            "model": "Bolero",
            "seating_capacity": 2,
            "fuel_type": "diesel",
            "registration_date": datetime.utcnow().isoformat(),
            "purchase_price": 1250000.00,
        },
        headers=auth_headers(token, org_id),
    )
    assert response.status_code == 201
    return response.json()


def create_booking(token: str, org_id: str, customer_id: int, vehicle_id: int):
    start = datetime.utcnow()
    end = start + timedelta(days=1)
    response = client.post(
        "/bookings/",
        json={
            "customer_id": customer_id,
            "vehicle_id": vehicle_id,
            "pickup_location": "Depot X",
            "destination": "Depot Y",
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "booking_amount": 8500.00,
        },
        headers=auth_headers(token, org_id),
    )
    assert response.status_code == 201
    return response.json()


def create_trip(token: str, org_id: str, booking_id: int, vehicle_id: int, status: str = "pending"):
    response = client.post(
        "/trips/",
        json={
            "booking_id": booking_id,
            "vehicle_id": vehicle_id,
            "start_km": 2000,
            "status": status,
        },
        headers=auth_headers(token, org_id),
    )
    assert response.status_code == 201
    return response.json()


def start_trip(token: str, org_id: str, trip_id: int):
    response = client.post(
        f"/trips/{trip_id}/start",
        headers=auth_headers(token, org_id),
    )
    assert response.status_code == 200
    return response.json()


def complete_trip(token: str, org_id: str, trip_id: int, end_km: int):
    response = client.post(
        f"/trips/{trip_id}/complete",
        json={"end_km": end_km},
        headers=auth_headers(token, org_id),
    )
    assert response.status_code == 200
    return response.json()


def test_expense_model_fields_present():
    columns = {col.name for col in models.Expense.__table__.columns}
    assert "trip_id" in columns
    assert "vehicle_id" in columns
    assert "category" in columns
    assert "amount" in columns
    assert "expense_date" in columns
    assert "description" in columns


def test_create_expense_directly_from_booking():
    org_name = f"expense-booking-org-{uuid.uuid4()}"
    org, token = create_org_and_admin(org_name, "expense_booking_admin@example.com", "SecurePass123")
    customer = create_customer(token, org["id"])
    vehicle = create_vehicle(token, org["id"])
    booking = create_booking(token, org["id"], customer["id"], vehicle["id"])

    expense_resp = client.post(
        "/expenses/",
        json={
            "booking_id": booking["id"],
            "category": "Fuel",
            "amount": 1250.00,
            "description": "Direct booking expense",
            "expense_date": datetime.utcnow().isoformat(),
        },
        headers=auth_headers(token, org["id"]),
    )
    assert expense_resp.status_code == 201
    expense = expense_resp.json()
    assert expense["booking_id"] == booking["id"]
    assert expense["trip_id"] is None
    assert expense["vehicle_id"] == vehicle["id"]


def test_create_expense_for_active_trip():
    org_name = f"expense-org-{uuid.uuid4()}"
    org, token = create_org_and_admin(org_name, "expense_admin@example.com", "SecurePass123")
    customer = create_customer(token, org["id"])
    vehicle = create_vehicle(token, org["id"])
    booking = create_booking(token, org["id"], customer["id"], vehicle["id"])
    trip = create_trip(token, org["id"], booking["id"], vehicle["id"], status="pending")
    started_trip = start_trip(token, org["id"], trip["id"])

    expense_resp = client.post(
        "/expenses/",
        json={
            "trip_id": started_trip["id"],
            "category": "Fuel",
            "amount": 2650.50,
            "description": "Fuel refill",
            "expense_date": datetime.utcnow().isoformat(),
        },
        headers=auth_headers(token, org["id"]),
    )
    assert expense_resp.status_code == 201
    expense = expense_resp.json()
    assert expense["trip_id"] == started_trip["id"]
    assert expense["vehicle_id"] == vehicle["id"]
    assert expense["category"] == "fuel"


def test_cannot_create_expense_for_cancelled_trip():
    org_name = f"expense-org-cancelled-{uuid.uuid4()}"
    org, token = create_org_and_admin(org_name, "expense_cancelled_admin@example.com", "SecurePass123")
    customer = create_customer(token, org["id"])
    vehicle = create_vehicle(token, org["id"])
    booking = create_booking(token, org["id"], customer["id"], vehicle["id"])
    cancelled_trip = create_trip(token, org["id"], booking["id"], vehicle["id"], status="cancelled")

    expense_resp = client.post(
        "/expenses/",
        json={
            "trip_id": cancelled_trip["id"],
            "category": "Toll",
            "amount": 450.00,
            "description": "Bridge toll",
            "expense_date": datetime.utcnow().isoformat(),
        },
        headers=auth_headers(token, org["id"]),
    )
    assert expense_resp.status_code == 400


def test_update_and_delete_expense():
    org_name = f"expense-org-update-{uuid.uuid4()}"
    org, token = create_org_and_admin(org_name, "expense_update_admin@example.com", "SecurePass123")
    customer = create_customer(token, org["id"])
    vehicle = create_vehicle(token, org["id"])
    booking = create_booking(token, org["id"], customer["id"], vehicle["id"])
    trip = create_trip(token, org["id"], booking["id"], vehicle["id"], status="completed")

    expense_resp = client.post(
        "/expenses/",
        json={
            "trip_id": trip["id"],
            "category": "Parking",
            "amount": 150.00,
            "description": "Lot parking",
            "expense_date": datetime.utcnow().isoformat(),
        },
        headers=auth_headers(token, org["id"]),
    )
    assert expense_resp.status_code == 201
    expense = expense_resp.json()

    update_resp = client.put(
        f"/expenses/{expense['id']}",
        json={"amount": 175.00, "description": "Lot parking fee"},
        headers=auth_headers(token, org["id"]),
    )
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["amount"] == 175.00
    assert updated["description"] == "Lot parking fee"

    delete_resp = client.delete(
        f"/expenses/{expense['id']}",
        headers=auth_headers(token, org["id"]),
    )
    assert delete_resp.status_code == 204

    get_resp = client.get(
        f"/expenses/{expense['id']}",
        headers=auth_headers(token, org["id"]),
    )
    assert get_resp.status_code == 404


def test_tenant_isolation_for_expenses():
    org_a_name = f"expense-org-a-{uuid.uuid4()}"
    org_b_name = f"expense-org-b-{uuid.uuid4()}"
    org_a, token_a = create_org_and_admin(org_a_name, "expense_a_admin@example.com", "SecurePass123")
    org_b, token_b = create_org_and_admin(org_b_name, "expense_b_admin@example.com", "SecurePass123")

    customer_a = create_customer(token_a, org_a["id"])
    vehicle_a = create_vehicle(token_a, org_a["id"])
    booking_a = create_booking(token_a, org_a["id"], customer_a["id"], vehicle_a["id"])
    trip_a = create_trip(token_a, org_a["id"], booking_a["id"], vehicle_a["id"], status="ongoing")

    expense_resp = client.post(
        "/expenses/",
        json={
            "trip_id": trip_a["id"],
            "category": "Maintenance",
            "amount": 950.00,
            "description": "Oil change",
            "expense_date": datetime.utcnow().isoformat(),
        },
        headers=auth_headers(token_a, org_a["id"]),
    )
    assert expense_resp.status_code == 201
    expense = expense_resp.json()

    forbidden_resp = client.get(
        f"/expenses/{expense['id']}",
        headers=auth_headers(token_b, org_b["id"]),
    )
    assert forbidden_resp.status_code == 404
