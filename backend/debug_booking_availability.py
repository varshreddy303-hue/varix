import uuid
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def auth_headers(token, org_id):
    return {"Authorization": f"Bearer {token}", "X-Organization-Id": org_id}

org_resp = client.post(
    "/auth/organizations/register",
    json={"name": "debug-org", "admin_email": "debug_admin@example.com", "admin_password": "SecurePass123"},
)
print('org_resp', org_resp.status_code, org_resp.text)
org = org_resp.json()
login_resp = client.post(
    "/auth/login",
    json={"organization_id": org['id'], "email": "debug_admin@example.com", "password": "SecurePass123"},
)
print('login_resp', login_resp.status_code, login_resp.text)
token = login_resp.json()['access_token']

customer_resp = client.post(
    "/customers/",
    json={"customer_name": "Debug Customer", "phone_number": "+911234567890", "email": "debug_customer@example.com"},
    headers=auth_headers(token, org['id']),
)
print('customer_resp', customer_resp.status_code, customer_resp.text)
customer = customer_resp.json()

vehicle_resp = client.post(
    "/vehicles/",
    json={
        "vehicle_number": "DBG-1234",
        "vehicle_type": "van",
        "make": "Tata",
        "model": "Ace",
        "seating_capacity": 6,
        "fuel_type": "diesel",
        "registration_date": datetime.utcnow().isoformat(),
        "purchase_price": 800000.0,
    },
    headers=auth_headers(token, org['id']),
)
print('vehicle_resp', vehicle_resp.status_code, vehicle_resp.text)
vehicle = vehicle_resp.json()

start = datetime.utcnow()
end = start + timedelta(days=2)
booking_resp = client.post(
    "/bookings/",
    json={
        "customer_id": customer['id'],
        "vehicle_id": vehicle['id'],
        "pickup_location": "Depot A",
        "destination": "Depot B",
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "booking_amount": 9000.0,
    },
    headers=auth_headers(token, org['id']),
)
print('booking_resp', booking_resp.status_code, booking_resp.text)
booking = booking_resp.json()

cancel_resp = client.post(
    f"/bookings/{booking['id']}/cancel",
    headers=auth_headers(token, org['id']),
)
print('cancel_resp', cancel_resp.status_code, cancel_resp.text)

availability_resp = client.get(
    "/bookings/availability",
    params={"vehicle_id": vehicle['id'], "start_date": start.isoformat(), "end_date": end.isoformat()},
    headers=auth_headers(token, org['id']),
)
print('availability_status', availability_resp.status_code)
print('availability_url', availability_resp.request.url)
print('availability_text', availability_resp.text)
print('availability_headers', availability_resp.headers)
