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
            "customer_name": "Invoice Customer",
            "phone_number": "+911234567891",
            "email": "invoice_customer@example.com",
        },
        headers=auth_headers(token, org_id),
    )
    assert response.status_code == 201
    return response.json()


def create_vehicle(token: str, org_id: str):
    response = client.post(
        "/vehicles/",
        json={
            "vehicle_number": "INV-1001",
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


def create_booking(token: str, org_id: str, customer_id: int, vehicle_id: int, start_offset_days: int = 0):
    start = datetime.utcnow() + timedelta(days=start_offset_days)
    end = start + timedelta(days=1)
    response = client.post(
        "/bookings/",
        json={
            "customer_id": customer_id,
            "vehicle_id": vehicle_id,
            "pickup_location": "Depot A",
            "destination": "Depot B",
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "booking_amount": 10000.00,
        },
        headers=auth_headers(token, org_id),
    )
    assert response.status_code == 201
    return response.json()


def create_completed_trip(token: str, org_id: str, booking_id: int, vehicle_id: int) -> dict:
    create_resp = client.post(
        "/trips/",
        json={
            "booking_id": booking_id,
            "vehicle_id": vehicle_id,
            "start_km": 1000,
            "km_rate": 150.0,
            "notes": "Completed trip for invoice test",
        },
        headers=auth_headers(token, org_id),
    )
    assert create_resp.status_code == 201
    trip = create_resp.json()

    complete_resp = client.post(
        f"/trips/{trip['id']}/complete",
        json={"end_km": 1050},
        headers=auth_headers(token, org_id),
    )
    assert complete_resp.status_code == 200
    return complete_resp.json()


def create_invoice(token: str, org_id: str, trip_id: int, invoice_number: str = None):
    payload = {"trip_id": trip_id}
    if invoice_number is not None:
        payload["invoice_number"] = invoice_number
    response = client.post(
        "/invoices/",
        json=payload,
        headers=auth_headers(token, org_id),
    )
    return response


def test_completed_trip_auto_creates_invoice_draft():
    org_name = f"invoice-org-{uuid.uuid4()}"
    org, token = create_org_and_admin(org_name, "invoice_admin@example.com", "SecurePass123")
    customer = create_customer(token, org["id"])
    vehicle = create_vehicle(token, org["id"])
    booking = create_booking(token, org["id"], customer["id"], vehicle["id"])
    trip = create_completed_trip(token, org["id"], booking["id"], vehicle["id"])

    invoices_resp = client.get(
        "/invoices",
        params={"trip_id": trip["id"]},
        headers=auth_headers(token, org["id"]),
    )
    assert invoices_resp.status_code == 200
    invoices = invoices_resp.json()
    assert len(invoices) == 1

    invoice = invoices[0]
    assert invoice["trip_id"] == trip["id"]
    assert invoice["customer_id"] == customer["id"]
    assert invoice["status"] == "draft"
    assert invoice["subtotal"] == 7500.0
    assert invoice["tax_amount"] == 0.0
    assert invoice["total_amount"] == 7500.0
    assert invoice["invoice_number"] == "10001"


def test_cannot_create_invoice_for_incomplete_trip():
    org_name = f"invoice-incomplete-{uuid.uuid4()}"
    org, token = create_org_and_admin(org_name, "invoice_incomplete_admin@example.com", "SecurePass123")
    customer = create_customer(token, org["id"])
    vehicle = create_vehicle(token, org["id"])
    booking = create_booking(token, org["id"], customer["id"], vehicle["id"])

    create_resp = client.post(
        "/trips/",
        json={
            "booking_id": booking["id"],
            "vehicle_id": vehicle["id"],
            "start_km": 1000,
            "trip_revenue": 5000.00,
        },
        headers=auth_headers(token, org["id"]),
    )
    assert create_resp.status_code == 201
    trip = create_resp.json()

    invoice_resp = create_invoice(token, org["id"], trip["id"])
    assert invoice_resp.status_code == 400
    assert invoice_resp.json()["detail"] == "Invoice can only be created for completed trips"


def test_send_and_mark_paid_invoice_flow():
    org_name = f"invoice-flow-{uuid.uuid4()}"
    org, token = create_org_and_admin(org_name, "invoice_flow_admin@example.com", "SecurePass123")
    customer = create_customer(token, org["id"])
    vehicle = create_vehicle(token, org["id"])
    booking = create_booking(token, org["id"], customer["id"], vehicle["id"])
    trip = create_completed_trip(token, org["id"], booking["id"], vehicle["id"])

    invoices_resp = client.get(
        "/invoices",
        params={"trip_id": trip["id"]},
        headers=auth_headers(token, org["id"]),
    )
    assert invoices_resp.status_code == 200
    invoice = invoices_resp.json()[0]

    send_resp = client.post(
        f"/invoices/{invoice['id']}/send",
        headers=auth_headers(token, org["id"]),
    )
    assert send_resp.status_code == 200
    assert send_resp.json()["status"] == "sent"

    paid_resp = client.post(
        f"/invoices/{invoice['id']}/mark-paid",
        headers=auth_headers(token, org["id"]),
    )
    assert paid_resp.status_code == 200
    assert paid_resp.json()["status"] == "paid"


def test_invoice_numbers_increment_for_sequential_trips():
    org_name = f"invoice-unique-{uuid.uuid4()}"
    org, token = create_org_and_admin(org_name, "invoice_unique_admin@example.com", "SecurePass123")
    customer = create_customer(token, org["id"])
    vehicle = create_vehicle(token, org["id"])
    booking = create_booking(token, org["id"], customer["id"], vehicle["id"])
    first_trip = create_completed_trip(token, org["id"], booking["id"], vehicle["id"])

    first_invoice_resp = client.get(
        "/invoices",
        params={"trip_id": first_trip["id"]},
        headers=auth_headers(token, org["id"]),
    )
    assert first_invoice_resp.status_code == 200
    assert first_invoice_resp.json()[0]["invoice_number"] == "10001"

    booking_2 = create_booking(token, org["id"], customer["id"], vehicle["id"], start_offset_days=2)
    second_trip = create_completed_trip(token, org["id"], booking_2["id"], vehicle["id"])

    second_invoice_resp = client.get(
        "/invoices",
        params={"trip_id": second_trip["id"]},
        headers=auth_headers(token, org["id"]),
    )
    assert second_invoice_resp.status_code == 200
    assert second_invoice_resp.json()[0]["invoice_number"] == "10002"


def test_can_create_invoice_from_booking_without_trip():
    org_name = f"invoice-booking-{uuid.uuid4()}"
    org, token = create_org_and_admin(org_name, "invoice_booking_admin@example.com", "SecurePass123")
    customer = create_customer(token, org["id"])
    vehicle = create_vehicle(token, org["id"])
    booking = create_booking(token, org["id"], customer["id"], vehicle["id"])

    response = client.post(
        "/invoices/",
        json={
            "booking_id": booking["id"],
            "invoice_number": "10099",
            "subtotal": 4500.0,
            "tax_amount": 450.0,
            "notes": "Booking-based invoice",
        },
        headers=auth_headers(token, org["id"]),
    )

    assert response.status_code == 201
    invoice = response.json()
    assert invoice["booking_id"] == booking["id"]
    assert invoice["trip_id"] is None
    assert invoice["customer_id"] == customer["id"]
    assert invoice["total_amount"] == 4950.0


def test_tenant_isolation_for_invoices():
    org_a_name = f"invoice-org-a-{uuid.uuid4()}"
    org_b_name = f"invoice-org-b-{uuid.uuid4()}"
    org_a, token_a = create_org_and_admin(org_a_name, "invoice_a_admin@example.com", "SecurePass123")
    org_b, token_b = create_org_and_admin(org_b_name, "invoice_b_admin@example.com", "SecurePass123")
    customer_a = create_customer(token_a, org_a["id"])
    vehicle_a = create_vehicle(token_a, org_a["id"])
    booking_a = create_booking(token_a, org_a["id"], customer_a["id"], vehicle_a["id"])
    trip_a = create_completed_trip(token_a, org_a["id"], booking_a["id"], vehicle_a["id"])

    invoices_resp = client.get(
        "/invoices",
        params={"trip_id": trip_a["id"]},
        headers=auth_headers(token_a, org_a["id"]),
    )
    assert invoices_resp.status_code == 200
    invoice = invoices_resp.json()[0]

    forbidden_resp = client.get(
        f"/invoices/{invoice['id']}",
        headers=auth_headers(token_b, org_b["id"]),
    )
    assert forbidden_resp.status_code == 404
