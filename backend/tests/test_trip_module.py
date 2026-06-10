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
            "vehicle_number": "TST-5678",
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


def create_booking(token: str, org_id: str, customer_id: int, vehicle_id: int):
    start = datetime.utcnow()
    end = start + timedelta(days=2)
    response = client.post(
        "/bookings/",
        json={
            "customer_id": customer_id,
            "vehicle_id": vehicle_id,
            "pickup_location": "Depot A",
            "destination": "Depot B",
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "booking_amount": 12000.00,
        },
        headers=auth_headers(token, org_id),
    )
    assert response.status_code == 201
    return response.json()


def create_package(token: str, org_id: str, package_data: dict):
    response = client.post("/trip-packages/", json=package_data, headers=auth_headers(token, org_id))
    assert response.status_code == 201
    return response.json()


def test_trip_model_fields_present():
    columns = {col.name for col in models.Trip.__table__.columns}
    assert "package_id" in columns
    assert "package_name" in columns
    assert "included_km" in columns
    assert "included_hours" in columns
    assert "extra_km" in columns
    assert "extra_hour_amount" in columns
    assert "grand_total" in columns


def test_create_start_and_complete_local_package_trip():
    org_name = f"trip-org-local-{uuid.uuid4()}"
    org, token = create_org_and_admin(org_name, "trip_admin_local@example.com", "SecurePass123")
    customer = create_customer(token, org["id"])
    vehicle = create_vehicle(token, org["id"])
    booking = create_booking(token, org["id"], customer["id"], vehicle["id"])

    package = create_package(
        token,
        org["id"],
        {
            "name": "Local 8hr/80km",
            "package_category": "Local",
            "included_hours": 8,
            "included_km": 80,
            "base_amount": 4200.0,
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
    )

    start = datetime.utcnow()
    end = start + timedelta(hours=5)
    create_resp = client.post(
        "/trips/",
        json={
            "booking_id": booking["id"],
            "vehicle_id": vehicle["id"],
            "package_id": package["id"],
            "start_km": 1000,
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "toll_amount": 200.0,
            "parking_amount": 100.0,
            "notes": "Local package trip",
        },
        headers=auth_headers(token, org["id"]),
    )
    assert create_resp.status_code == 201
    trip = create_resp.json()
    assert trip["package_name"] == "Local 8hr/80km"
    assert trip["grand_total"] == 5950.0
    assert trip["distance_km"] is None

    start_resp = client.post(f"/trips/{trip['id']}/start", headers=auth_headers(token, org["id"]))
    assert start_resp.status_code == 200
    started_trip = start_resp.json()
    assert started_trip["status"] == "ongoing"

    complete_resp = client.post(
        f"/trips/{trip['id']}/complete",
        json={"end_km": 1080, "end_time": end.isoformat()},
        headers=auth_headers(token, org["id"]),
    )
    assert complete_resp.status_code == 200
    completed_trip = complete_resp.json()
    assert completed_trip["status"] == "completed"
    assert completed_trip["distance_km"] == 80.0
    assert completed_trip["extra_km"] == 0.0
    assert completed_trip["extra_hours"] == 0.0
    assert completed_trip["grand_total"] == 5950.0


def test_300km_average_package_calculation():
    org_name = f"trip-org-300km-{uuid.uuid4()}"
    org, token = create_org_and_admin(org_name, "trip_admin_300@example.com", "SecurePass123")
    customer = create_customer(token, org["id"])
    vehicle = create_vehicle(token, org["id"])
    booking = create_booking(token, org["id"], customer["id"], vehicle["id"])

    package = create_package(
        token,
        org["id"],
        {
            "name": "300 KM Average",
            "package_category": "300 KM Average",
            "minimum_km_per_day": 300,
            "base_amount": 10500.0,
            "extra_km_rate": 45.0,
            "driver_bata_default": 500.0,
            "night_charge_default": 600.0,
            "active": True,
        },
    )

    start = datetime.utcnow()
    end = start + timedelta(days=2)
    create_resp = client.post(
        "/trips/",
        json={
            "booking_id": booking["id"],
            "vehicle_id": vehicle["id"],
            "package_id": package["id"],
            "start_km": 1000,
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "toll_amount": 250.0,
            "parking_amount": 150.0,
            "notes": "300 km average trip",
        },
        headers=auth_headers(token, org["id"]),
    )
    assert create_resp.status_code == 201

    complete_resp = client.post(
        f"/trips/{create_resp.json()['id']}/complete",
        json={"end_km": 2000, "end_time": end.isoformat()},
        headers=auth_headers(token, org["id"]),
    )
    assert complete_resp.status_code == 200
    completed_trip = complete_resp.json()
    assert completed_trip["days_used"] == 3
    assert completed_trip["included_km"] == 900
    assert completed_trip["extra_km"] == 100.0
    assert completed_trip["grand_total"] == 16500.0


def test_outstation_package_calculation():
    org_name = f"trip-org-outstation-{uuid.uuid4()}"
    org, token = create_org_and_admin(org_name, "trip_admin_outstation@example.com", "SecurePass123")
    customer = create_customer(token, org["id"])
    vehicle = create_vehicle(token, org["id"])
    booking = create_booking(token, org["id"], customer["id"], vehicle["id"])

    package = create_package(
        token,
        org["id"],
        {
            "name": "Outstation Standard",
            "package_category": "Outstation",
            "km_rate": 20.0,
            "driver_bata_default": 500.0,
            "night_charge_default": 600.0,
            "permit_default": 200.0,
            "state_tax_default": 150.0,
            "active": True,
        },
    )

    create_resp = client.post(
        "/trips/",
        json={
            "booking_id": booking["id"],
            "vehicle_id": vehicle["id"],
            "package_id": package["id"],
            "start_km": 2000,
            "start_time": datetime.utcnow().isoformat(),
            "notes": "Outstation trip",
        },
        headers=auth_headers(token, org["id"]),
    )
    assert create_resp.status_code == 201

    complete_resp = client.post(
        f"/trips/{create_resp.json()['id']}/complete",
        json={"end_km": 2500},
        headers=auth_headers(token, org["id"]),
    )
    assert complete_resp.status_code == 200
    completed_trip = complete_resp.json()
    assert completed_trip["distance_km"] == 500.0
    assert completed_trip["grand_total"] == 11450.0


def test_negative_km_and_negative_time_rejected():
    org_name = f"trip-org-edge-{uuid.uuid4()}"
    org, token = create_org_and_admin(org_name, "trip_admin_edge@example.com", "SecurePass123")
    customer = create_customer(token, org["id"])
    vehicle = create_vehicle(token, org["id"])
    booking = create_booking(token, org["id"], customer["id"], vehicle["id"])

    package = create_package(
        token,
        org["id"],
        {
            "name": "Local Min",
            "package_category": "Local",
            "included_hours": 4,
            "included_km": 40,
            "base_amount": 2800.0,
            "extra_km_rate": 45.0,
            "extra_hour_rate": 400.0,
            "active": True,
        },
    )

    invalid_km_resp = client.post(
        "/trips/",
        json={
            "booking_id": booking["id"],
            "vehicle_id": vehicle["id"],
            "package_id": package["id"],
            "start_km": 100,
            "end_km": 90,
        },
        headers=auth_headers(token, org["id"]),
    )
    assert invalid_km_resp.status_code == 400

    start = datetime.utcnow()
    end = start - timedelta(hours=1)
    invalid_time_resp = client.post(
        "/trips/",
        json={
            "booking_id": booking["id"],
            "vehicle_id": vehicle["id"],
            "package_id": package["id"],
            "start_km": 100,
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
        },
        headers=auth_headers(token, org["id"]),
    )
    assert invalid_time_resp.status_code == 400


def test_multi_day_300km_average_edge_case():
    org_name = f"trip-org-multiday-{uuid.uuid4()}"
    org, token = create_org_and_admin(org_name, "trip_admin_multiday@example.com", "SecurePass123")
    customer = create_customer(token, org["id"])
    vehicle = create_vehicle(token, org["id"])
    booking = create_booking(token, org["id"], customer["id"], vehicle["id"])

    package = create_package(
        token,
        org["id"],
        {
            "name": "300 KM Average",
            "package_category": "300 KM Average",
            "minimum_km_per_day": 300,
            "base_amount": 15000.0,
            "extra_km_rate": 50.0,
            "active": True,
        },
    )

    start = datetime.utcnow()
    end = start + timedelta(days=4)
    create_resp = client.post(
        "/trips/",
        json={
            "booking_id": booking["id"],
            "vehicle_id": vehicle["id"],
            "package_id": package["id"],
            "start_km": 1000,
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
        },
        headers=auth_headers(token, org["id"]),
    )
    assert create_resp.status_code == 201

    complete_resp = client.post(
        f"/trips/{create_resp.json()['id']}/complete",
        json={"end_km": 2500, "end_time": end.isoformat()},
        headers=auth_headers(token, org["id"]),
    )
    assert complete_resp.status_code == 200
    completed_trip = complete_resp.json()
    assert completed_trip["days_used"] == 5
    assert completed_trip["included_km"] == 1500
    assert completed_trip["extra_km"] == 0.0
    assert completed_trip["grand_total"] == 15000.0


def test_tenant_isolation_for_trips():
    org_a_name = f"trip-org-a-{uuid.uuid4()}"
    org_b_name = f"trip-org-b-{uuid.uuid4()}"
    org_a, token_a = create_org_and_admin(org_a_name, "trip_a_admin@example.com", "SecurePass123")
    org_b, token_b = create_org_and_admin(org_b_name, "trip_b_admin@example.com", "SecurePass123")

    customer_a = create_customer(token_a, org_a["id"])
    vehicle_a = create_vehicle(token_a, org_a["id"])
    booking_a = create_booking(token_a, org_a["id"], customer_a["id"], vehicle_a["id"])

    trip_resp = client.post(
        "/trips/",
        json={
            "booking_id": booking_a["id"],
            "vehicle_id": vehicle_a["id"],
            "start_km": 1800,
        },
        headers=auth_headers(token_a, org_a["id"]),
    )
    assert trip_resp.status_code == 201
    trip = trip_resp.json()

    forbidden_resp = client.get(
        f"/trips/{trip['id']}",
        headers=auth_headers(token_b, org_b["id"]),
    )
    assert forbidden_resp.status_code == 404
