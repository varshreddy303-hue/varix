from datetime import datetime, timedelta
from fastapi.testclient import TestClient
import sys
sys.path.append('backend')
from app.main import app

client = TestClient(app)
org_resp = client.post('/auth/organizations/register', json={'name':'tmp-org','admin_email':'tmp@example.com','admin_password':'SecurePass123'})
print('org', org_resp.status_code, org_resp.text)
org = org_resp.json()
login = client.post('/auth/login', json={'organization_id': org['id'], 'email': 'tmp@example.com', 'password': 'SecurePass123'})
print('login', login.status_code, login.text)
token = login.json()['access_token']
headers = {'Authorization': f'Bearer {token}', 'X-Organization-Id': org['id']}
cust = client.post('/customers/', json={'customer_name':'C','phone_number':'+911234567890','email':'cust@example.com'}, headers=headers).json()
veh = client.post('/vehicles/', json={'vehicle_number':'TST-9999','vehicle_type':'van','make':'Tata','model':'Ace','seating_capacity':6,'fuel_type':'diesel','registration_date': datetime.utcnow().isoformat(),'purchase_price':800000.0}, headers=headers).json()
start = datetime.utcnow(); end = start + timedelta(days=2)
bk = client.post('/bookings/', json={'customer_id': cust['id'], 'vehicle_id': veh['id'], 'pickup_location':'A','destination':'B','start_date': start.isoformat(),'end_date': end.isoformat(),'booking_amount':12000.0}, headers=headers).json()
package = client.post('/trip-packages/', json={'name':'Outstation Standard','package_category':'Outstation','km_rate':20.0,'driver_bata_default':500.0,'night_charge_default':600.0,'permit_default':200.0,'state_tax_default':150.0,'active':True}, headers=headers).json()
print('package', package)
trip = client.post('/trips/', json={'booking_id': bk['id'], 'vehicle_id': veh['id'], 'package_id': package['id'],'start_km':2000,'start_time': datetime.utcnow().isoformat(),'notes':'Outstation trip'}, headers=headers).json()
print('trip create', trip)
complete = client.post(f"/trips/{trip['id']}/complete", json={'end_km':2500}, headers=headers).json()
print('trip complete', complete)
