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
            "customer_name": "Profit Customer",
            "phone_number": "+911234567892",
            "email": "profit_customer@example.com",
        },
        headers=auth_headers(token, org_id),
    )
    assert response.status_code == 201
    return response.json()


def create_vehicle(token: str, org_id: str):
    response = client.post(
        "/vehicles/",
        json={
            "vehicle_number": "PRF-001",
            "vehicle_type": "sedan",
            "make": "Hyundai",
            "model": "Verna",
            "seating_capacity": 4,
            "fuel_type": "petrol",
            "registration_date": datetime.utcnow().isoformat(),
            "purchase_price": 1200000.00,
        },
        headers=auth_headers(token, org_id),
    )
    assert response.status_code == 201
    return response.json()


def create_booking(token: str, org_id: str, customer_id: int, vehicle_id: int):
    start = datetime.utcnow()
    end = start + timedelta(days=2)
    response = client.post(
        "/bookings/",
        json={
            "customer_id": customer_id,
            "vehicle_id": vehicle_id,
            "pickup_location": "Office",
            "destination": "Warehouse",
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "booking_amount": 15000.00,
        },
        headers=auth_headers(token, org_id),
    )
    assert response.status_code == 201
    return response.json()


def create_trip(token: str, org_id: str, booking_id: int, vehicle_id: int, trip_revenue: float):
    response = client.post(
        "/trips/",
        json={
            "booking_id": booking_id,
            "vehicle_id": vehicle_id,
            "start_km": 1000,
            "trip_revenue": trip_revenue,
        },
        headers=auth_headers(token, org_id),
    )
    assert response.status_code == 201
    return response.json()


def create_expense(token: str, org_id: str, trip_id: int, category: str, amount: float):
    response = client.post(
        "/expenses/",
        json={
            "trip_id": trip_id,
            "category": category,
            "amount": amount,
            "description": "Profit test expense",
            "expense_date": datetime.utcnow().isoformat(),
        },
        headers=auth_headers(token, org_id),
    )
    assert response.status_code == 201
    return response.json()


def test_profit_calculation_and_summary():
    org_name = f"profit-org-{uuid.uuid4()}"
    org, token = create_org_and_admin(org_name, "profit_admin@example.com", "SecurePass123")
    customer = create_customer(token, org["id"])
    vehicle = create_vehicle(token, org["id"])
    booking = create_booking(token, org["id"], customer["id"], vehicle["id"])
    trip = create_trip(token, org["id"], booking["id"], vehicle["id"], trip_revenue=12000.00)

    expense = create_expense(token, org["id"], trip["id"], "Fuel", 2200.00)
    expense2 = create_expense(token, org["id"], trip["id"], "Toll", 300.00)

    profit_resp = client.get(
        f"/profits/trip/{trip['id']}",
        headers=auth_headers(token, org["id"]),
    )
    assert profit_resp.status_code == 200
    profit = profit_resp.json()
    assert profit["trip_id"] == trip["id"]
    assert profit["vehicle_id"] == vehicle["id"]
    assert profit["trip_revenue"] == 12000.00
    assert profit["total_expense"] == 2500.00
    assert profit["trip_profit"] == 9500.00

    daily_resp = client.get(
        f"/profits/vehicle/{vehicle['id']}/daily",
        headers=auth_headers(token, org["id"]),
    )
    assert daily_resp.status_code == 200
    daily = daily_resp.json()
    assert len(daily) == 1
    assert daily[0]["total_profit"] == 9500.00

    monthly_resp = client.get(
        f"/profits/vehicle/{vehicle['id']}/monthly",
        headers=auth_headers(token, org["id"]),
    )
    assert monthly_resp.status_code == 200
    monthly = monthly_resp.json()
    assert len(monthly) == 1
    assert monthly[0]["total_revenue"] == 12000.00
    assert monthly[0]["total_expense"] == 2500.00
    assert monthly[0]["total_profit"] == 9500.00

    summary_resp = client.get(
        "/profits/summary",
        headers=auth_headers(token, org["id"]),
    )
    assert summary_resp.status_code == 200
    summary = summary_resp.json()
    assert summary["total_revenue"] == 12000.00
    assert summary["total_expense"] == 2500.00
    assert summary["total_profit"] == 9500.00


def test_profit_recalculation_on_expense_update_and_delete():
    org_name = f"profit-update-org-{uuid.uuid4()}"
    org, token = create_org_and_admin(org_name, "profit_update_admin@example.com", "SecurePass123")
    customer = create_customer(token, org["id"])
    vehicle = create_vehicle(token, org["id"])
    booking = create_booking(token, org["id"], customer["id"], vehicle["id"])
    trip = create_trip(token, org["id"], booking["id"], vehicle["id"], trip_revenue=8000.00)

    expense = create_expense(token, org["id"], trip["id"], "Parking", 400.00)

    updated_resp = client.put(
        f"/expenses/{expense['id']}",
        json={"amount": 500.00},
        headers=auth_headers(token, org["id"]),
    )
    assert updated_resp.status_code == 200
    updated = updated_resp.json()
    assert updated["amount"] == 500.00

    profit_resp = client.get(
        f"/profits/trip/{trip['id']}",
        headers=auth_headers(token, org["id"]),
    )
    assert profit_resp.status_code == 200
    assert profit_resp.json()["trip_profit"] == 7500.00

    delete_resp = client.delete(
        f"/expenses/{expense['id']}",
        headers=auth_headers(token, org["id"]),
    )
    assert delete_resp.status_code == 204

    profit_resp = client.get(
        f"/profits/trip/{trip['id']}",
        headers=auth_headers(token, org["id"]),
    )
    assert profit_resp.status_code == 200
    assert profit_resp.json()["total_expense"] == 0.0
    assert profit_resp.json()["trip_profit"] == 8000.00
