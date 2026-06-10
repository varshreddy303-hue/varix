import { useEffect, useMemo, useState } from 'react';
import { Plus, Search, Edit3, Eye, Trash2 } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { BookingForm } from '../components/bookings/BookingForm';
import { fetchBookings, createBooking, updateBooking, deleteBooking } from '../services/bookingService';
import { fetchCustomers } from '../services/customerService';
import { fetchVehicles } from '../services/vehicleService';
import type { Booking, Customer, Vehicle } from '../types';

function formatDate(value: string) {
  return new Date(value).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
}

function statusClass(status: string) {
  if (status.toLowerCase() === 'active') return 'bg-emerald-100 text-emerald-700';
  if (status.toLowerCase() === 'completed') return 'bg-sky-100 text-sky-700';
  if (status.toLowerCase() === 'cancelled') return 'bg-red-100 text-red-700';
  return 'bg-slate-100 text-slate-700';
}

function formatCurrency(amount: number) {
  return `₹${amount.toLocaleString()}`;
}

export function Bookings() {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [activeBooking, setActiveBooking] = useState<Booking | undefined>(undefined);
  const [detailsBooking, setDetailsBooking] = useState<Booking | undefined>(undefined);

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
      } catch (err) {
        setError('Unable to load bookings. Please try again.');
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  const bookingsWithLabels = useMemo(() => {
    const customerMap = new Map(customers.map((customer) => [customer.id, customer]));
    const vehicleMap = new Map(vehicles.map((vehicle) => [vehicle.id, vehicle]));

    return bookings.map((booking) => ({
      ...booking,
      customerName: booking.customerName || customerMap.get(booking.customerId ?? '')?.name || 'Unknown',
      vehicleLabel: vehicleMap.get(booking.vehicleId)?.licensePlate ?? 'Unknown',
    }));
  }, [bookings, customers, vehicles]);

  const filteredBookings = useMemo(() => {
    const normalized = search.toLowerCase().trim();
    return bookingsWithLabels.filter((booking) =>
      [booking.customerName, booking.vehicleLabel, booking.pickupLocation, booking.destination, booking.status]
        .join(' ')
        .toLowerCase()
        .includes(normalized),
    );
  }, [bookingsWithLabels, search]);

  async function refresh() {
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
      setError('Unable to refresh bookings.');
    } finally {
      setLoading(false);
    }
  }

  async function handleSaveBooking(payload: Omit<Booking, 'id'>) {
    if (activeBooking) {
      await updateBooking(activeBooking.id, payload);
    } else {
      await createBooking(payload);
    }
    await refresh();
  }

  async function handleCancelBooking(bookingId: string) {
    const confirmed = window.confirm('Cancel this booking?');
    if (!confirmed) return;

    setLoading(true);
    setError('');
    try {
      await deleteBooking(bookingId);
      await refresh();
    } catch {
      setError('Unable to cancel booking.');
      setLoading(false);
    }
  }

  const customerMap = useMemo(() => new Map(customers.map((customer) => [customer.id, customer])), [customers]);
  const vehicleMap = useMemo(() => new Map(vehicles.map((vehicle) => [vehicle.id, vehicle])), [vehicles]);

  return (
    <div className="space-y-6">
      <div className="rounded-3xl bg-white p-6 shadow-sm shadow-slate-200/80 sm:flex sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Bookings</h1>
          <p className="mt-1 text-sm text-slate-600">Manage customer bookings and monitor trip schedules.</p>
        </div>
        <div className="mt-4 flex flex-col gap-3 sm:mt-0 sm:flex-row sm:items-center">
          <Button onClick={() => { setActiveBooking(undefined); setModalOpen(true); }}>
            <Plus className="mr-2 h-4 w-4" />
            Create booking
          </Button>
          <Button variant="secondary" onClick={refresh} disabled={loading}>
            Refresh
          </Button>
        </div>
      </div>

      <Card>
        <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="relative w-full max-w-md">
            <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <Input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search bookings"
              className="pl-11"
            />
          </div>
          <p className="text-sm text-slate-500">
            {loading ? 'Loading bookings…' : `${filteredBookings.length} booking${filteredBookings.length === 1 ? '' : 's'}`}
          </p>
        </div>

        {error && (
          <div className="mb-6 rounded-3xl bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        {loading ? (
          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-10 text-center text-slate-500">
            Loading bookings...
          </div>
        ) : filteredBookings.length === 0 ? (
          <div className="rounded-3xl border border-dashed border-slate-200 bg-slate-50 p-10 text-center text-slate-500">
            <p className="mb-3 text-lg font-semibold text-slate-900">No bookings found</p>
            <p>Use the Create booking button to add a new reservation.</p>
          </div>
        ) : (
          <div className="overflow-hidden rounded-3xl border border-slate-200">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
                <thead className="bg-slate-50 text-slate-600">
                  <tr>
                    <th className="px-6 py-4 font-medium">Customer</th>
                    <th className="px-6 py-4 font-medium">Vehicle</th>
                    <th className="px-6 py-4 font-medium">Pickup</th>
                    <th className="px-6 py-4 font-medium">Destination</th>
                    <th className="px-6 py-4 font-medium">Start</th>
                    <th className="px-6 py-4 font-medium">End</th>
                    <th className="px-6 py-4 font-medium">Amount</th>
                    <th className="px-6 py-4 font-medium">Status</th>
                    <th className="px-6 py-4 font-medium text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 bg-white">
                  {filteredBookings.map((booking) => (
                    <tr key={booking.id} className="hover:bg-slate-50">
                      <td className="px-6 py-4 font-medium text-slate-900">{booking.customerName}</td>
                      <td className="px-6 py-4 text-slate-600">{booking.vehicleLabel}</td>
                      <td className="px-6 py-4 text-slate-600">{booking.pickupLocation}</td>
                      <td className="px-6 py-4 text-slate-600">{booking.destination}</td>
                      <td className="px-6 py-4 text-slate-600">{formatDate(booking.startDate)}</td>
                      <td className="px-6 py-4 text-slate-600">{formatDate(booking.endDate)}</td>
                      <td className="px-6 py-4 text-slate-600">{formatCurrency(booking.amount)}</td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${statusClass(booking.status)}`}>
                          {booking.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="inline-flex flex-wrap items-center justify-end gap-2">
                          <Button
                            type="button"
                            variant="secondary"
                            className="inline-flex items-center gap-2"
                            onClick={() => setDetailsBooking(booking)}
                          >
                            <Eye className="h-4 w-4" />
                            View
                          </Button>
                          <Button
                            type="button"
                            variant="secondary"
                            className="inline-flex items-center gap-2"
                            onClick={() => {
                              setActiveBooking(booking);
                              setModalOpen(true);
                            }}
                          >
                            <Edit3 className="h-4 w-4" />
                            Edit
                          </Button>
                          <Button
                            type="button"
                            variant="ghost"
                            className="text-red-600 hover:bg-red-50"
                            onClick={() => handleCancelBooking(booking.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                            Cancel
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </Card>

      <BookingForm
        open={modalOpen}
        booking={activeBooking}
        customers={customers}
        vehicles={vehicles}
        bookings={bookings}
        onClose={() => setModalOpen(false)}
        onSave={handleSaveBooking}
      />

      {detailsBooking && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/40 px-4 py-6">
          <div className="w-full max-w-2xl rounded-3xl bg-white p-6 shadow-2xl shadow-slate-900/10">
            <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 className="text-xl font-semibold text-slate-900">Booking details</h2>
                <p className="text-sm text-slate-500">Review the trip and customer information.</p>
              </div>
              <Button type="button" variant="ghost" onClick={() => setDetailsBooking(undefined)}>
                Close
              </Button>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-sm text-slate-500">Customer</p>
                <p className="mt-2 font-semibold text-slate-900">{detailsBooking.customerName || customerMap.get(detailsBooking.customerId ?? '')?.name || 'Unknown'}</p>
              </div>
              <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-sm text-slate-500">Vehicle</p>
                <p className="mt-2 font-semibold text-slate-900">{vehicleMap.get(detailsBooking.vehicleId)?.licensePlate ?? 'Unknown'}</p>
              </div>
              <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-sm text-slate-500">Pickup</p>
                <p className="mt-2 font-semibold text-slate-900">{detailsBooking.pickupLocation}</p>
              </div>
              <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-sm text-slate-500">Destination</p>
                <p className="mt-2 font-semibold text-slate-900">{detailsBooking.destination}</p>
              </div>
              <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-sm text-slate-500">Dates</p>
                <p className="mt-2 font-semibold text-slate-900">{formatDate(detailsBooking.startDate)} – {formatDate(detailsBooking.endDate)}</p>
              </div>
              <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-sm text-slate-500">Amount</p>
                <p className="mt-2 font-semibold text-slate-900">{formatCurrency(detailsBooking.amount)}</p>
              </div>
              <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4 sm:col-span-2">
                <p className="text-sm text-slate-500">Status</p>
                <span className={`mt-2 inline-flex rounded-full px-3 py-1 text-xs font-semibold ${statusClass(detailsBooking.status)}`}>
                  {detailsBooking.status}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
