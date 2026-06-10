import { useEffect, useMemo, useState } from 'react';
import { Printer, Truck } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { fetchBookings } from '../services/bookingService';
import { fetchCustomers } from '../services/customerService';
import { fetchVehicles } from '../services/vehicleService';
import type { Booking, Customer, Vehicle } from '../types';

function formatDate(value: string) {
  return new Date(value).toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

function formatTime(value: string) {
  return new Date(value).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
}

function buildDutySlip(booking: Booking, customer: Customer | undefined, vehicle: Vehicle | undefined) {
  return `
    <html>
      <head>
        <title>Duty Slip</title>
        <style>
          body { font-family: Arial, sans-serif; padding: 24px; color: #111827; }
          h1 { font-size: 24px; margin-bottom: 12px; }
          .section { margin-bottom: 18px; }
          .label { display: block; font-size: 12px; color: #6b7280; margin-bottom: 6px; }
          .value { font-size: 16px; font-weight: 600; margin-bottom: 4px; }
          .box { border: 1px solid #e2e8f0; border-radius: 16px; padding: 16px; }
        </style>
      </head>
      <body>
        <h1>Duty Slip</h1>
        <div class="box">
          <div class="section">
            <span class="label">Booking ID</span>
            <div class="value">${booking.id}</div>
          </div>
          <div class="section">
            <span class="label">Customer</span>
            <div class="value">${customer?.name ?? 'Unknown'}</div>
          </div>
          <div class="section">
            <span class="label">Vehicle</span>
            <div class="value">${vehicle?.licensePlate ?? 'Unknown'}</div>
          </div>
          <div class="section">
            <span class="label">Pickup</span>
            <div class="value">${booking.pickupLocation}</div>
          </div>
          <div class="section">
            <span class="label">Destination</span>
            <div class="value">${booking.destination}</div>
          </div>
          <div class="section">
            <span class="label">Schedule</span>
            <div class="value">${formatDate(booking.startDate)} → ${formatDate(booking.endDate)}</div>
          </div>
          <div class="section">
            <span class="label">Status</span>
            <div class="value">${booking.status}</div>
          </div>
          <div class="section">
            <span class="label">Amount</span>
            <div class="value">₹${booking.amount.toLocaleString()}</div>
          </div>
        </div>
      </body>
    </html>
  `;
}

function printDutySlip(booking: Booking, customer: Customer | undefined, vehicle: Vehicle | undefined) {
  const slip = buildDutySlip(booking, customer, vehicle);
  const printWindow = window.open('', '_blank');
  if (!printWindow) {
    return;
  }
  printWindow.document.write(slip);
  printWindow.document.close();
  printWindow.focus();
  setTimeout(() => printWindow.print(), 250);
}

export function Dispatch() {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      setError('');
      try {
        const [bookingsData, customersData, vehiclesData] = await Promise.all([
          fetchBookings(),
          fetchCustomers(),
          fetchVehicles(),
        ]);
        setBookings(bookingsData);
        setCustomers(customersData);
        setVehicles(vehiclesData);
      } catch {
        setError('Unable to load dispatch queue.');
      } finally {
        setLoading(false);
      }
    }

    void loadData();
  }, []);

  const customerMap = useMemo(() => new Map(customers.map((customer) => [customer.id, customer])), [customers]);
  const vehicleMap = useMemo(() => new Map(vehicles.map((vehicle) => [vehicle.id, vehicle])), [vehicles]);

  const filteredBookings = useMemo(() => {
    const normalized = search.toLowerCase().trim();
    return bookings.filter((booking) => {
      const customer = customerMap.get(booking.customerId ?? '')?.name ?? booking.customerName ?? '';
      const vehicle = vehicleMap.get(booking.vehicleId)?.licensePlate ?? '';
      return [customer, vehicle, booking.pickupLocation, booking.destination, booking.status]
        .join(' ')
        .toLowerCase()
        .includes(normalized);
    });
  }, [bookings, customerMap, vehicleMap, search]);

  return (
    <div className="space-y-6">
      <div className="rounded-3xl bg-white p-6 shadow-sm shadow-slate-200/80 sm:flex sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Dispatch</h1>
          <p className="mt-1 text-sm text-slate-600">Review upcoming bookings and print duty slips for vehicle dispatch.</p>
        </div>
        <div className="mt-4 flex flex-col gap-3 sm:mt-0 sm:flex-row sm:items-center">
          <Button onClick={() => window.location.reload()}>Refresh</Button>
        </div>
      </div>

      <Card>
        <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="relative w-full max-w-md">
            <Input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search dispatch bookings"
              className="pl-4"
            />
          </div>
          <p className="text-sm text-slate-500">{loading ? 'Loading dispatch queue…' : `${filteredBookings.length} assignments`}</p>
        </div>

        {error && (
          <div className="mb-6 rounded-3xl bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
        )}

        {loading ? (
          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-10 text-center text-slate-500">Loading dispatch items...</div>
        ) : filteredBookings.length === 0 ? (
          <div className="rounded-3xl border border-dashed border-slate-200 bg-slate-50 p-10 text-center text-slate-500">
            No upcoming dispatch assignments.
          </div>
        ) : (
          <div className="space-y-4">
            {filteredBookings.map((booking) => (
              <div key={booking.id} className="rounded-3xl border border-slate-200 bg-white p-4 shadow-sm shadow-slate-100">
                <div className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
                  <div>
                    <p className="text-sm text-slate-500">Booking</p>
                    <p className="text-lg font-semibold text-slate-900">{customerMap.get(booking.customerId ?? '')?.name ?? booking.customerName ?? 'Unknown customer'}</p>
                    <p className="text-sm text-slate-500">{vehicleMap.get(booking.vehicleId)?.licensePlate ?? 'Unknown vehicle'}</p>
                    <p className="mt-2 text-slate-600">{booking.pickupLocation} → {booking.destination}</p>
                    <p className="mt-2 text-slate-600">{formatDate(booking.startDate)} – {formatDate(booking.endDate)}</p>
                  </div>
                  <div className="flex flex-col justify-between gap-4 text-right">
                    <div>
                      <p className="text-sm text-slate-500">Status</p>
                      <p className="font-semibold text-slate-900">{booking.status}</p>
                    </div>
                    <Button type="button" onClick={() => printDutySlip(booking, customerMap.get(booking.customerId ?? '') ?? undefined, vehicleMap.get(booking.vehicleId))}>
                      <Printer className="mr-2 h-4 w-4" />
                      Duty slip
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
