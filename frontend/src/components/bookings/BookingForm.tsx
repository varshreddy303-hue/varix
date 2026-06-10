import { useEffect, useMemo, useState } from 'react';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { getApiErrorMessage } from '../../lib/api';
import type { Booking, Customer, Vehicle } from '../../types';

interface BookingFormProps {
  open: boolean;
  booking?: Booking;
  customers: Customer[];
  vehicles: Vehicle[];
  bookings: Booking[];
  onClose: () => void;
  onSave: (payload: Omit<Booking, 'id'>) => Promise<void>;
}

function overlap(startA: string, endA: string, startB: string, endB: string) {
  return !(new Date(endA) < new Date(startB) || new Date(startA) > new Date(endB));
}

export function BookingForm({ open, booking, customers, vehicles, bookings, onClose, onSave }: BookingFormProps) {
  const [customerId, setCustomerId] = useState('');
  const [customerName, setCustomerName] = useState('');
  const [customerCompany, setCustomerCompany] = useState('');
  const [customerPhone, setCustomerPhone] = useState('');
  const [customerEmail, setCustomerEmail] = useState('');
  const [customerGstNumber, setCustomerGstNumber] = useState('');
  const [customerCity, setCustomerCity] = useState('');
  const [customerNotes, setCustomerNotes] = useState('');
  const [vehicleId, setVehicleId] = useState('');
  const [pickupLocation, setPickupLocation] = useState('');
  const [destination, setDestination] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [amount, setAmount] = useState(0);
  const [status, setStatus] = useState('active');
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (booking) {
      setCustomerId(booking.customerId ?? '');
      setCustomerName(booking.customerName ?? '');
      setCustomerCompany(booking.customerCompany ?? '');
      setCustomerPhone(booking.customerPhone ?? '');
      setCustomerEmail(booking.customerEmail ?? '');
      setCustomerGstNumber(booking.customerGstNumber ?? '');
      setCustomerCity(booking.customerCity ?? '');
      setCustomerNotes(booking.customerNotes ?? '');
      setVehicleId(booking.vehicleId);
      setPickupLocation(booking.pickupLocation);
      setDestination(booking.destination);
      setStartDate(booking.startDate);
      setEndDate(booking.endDate);
      setAmount(booking.amount);
      setStatus(booking.status ?? 'active');
      setError('');
    } else {
      setCustomerId('');
      setCustomerName('');
      setCustomerCompany('');
      setCustomerPhone('');
      setCustomerEmail('');
      setCustomerGstNumber('');
      setCustomerCity('');
      setCustomerNotes('');
      setVehicleId('');
      setPickupLocation('');
      setDestination('');
      setStartDate('');
      setEndDate('');
      setAmount(0);
      setStatus('active');
      setError('');
    }
  }, [booking, open, customers]);

  const availableVehicles = useMemo(() => {
    if (!startDate || !endDate) {
      return vehicles;
    }

    return vehicles.filter((vehicle) => {
      const vehicleBookings = bookings.filter((item) => item.vehicleId === vehicle.id && item.id !== booking?.id);
      return !vehicleBookings.some((item) => overlap(startDate, endDate, item.startDate, item.endDate));
    });
  }, [vehicles, bookings, startDate, endDate, booking]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError('');
    setSaving(true);

    if (!vehicleId || !pickupLocation || !destination || !startDate || !endDate || amount <= 0) {
      setError('Please complete all required fields.');
      setSaving(false);
      return;
    }

    if (!customerId && !customerName.trim() && !customerPhone.trim()) {
      setError('Add a customer name or phone number for booking-first reservations.');
      setSaving(false);
      return;
    }

    if (new Date(endDate) < new Date(startDate)) {
      setError('End date must be the same or later than start date.');
      setSaving(false);
      return;
    }

    try {
      await onSave({
        customerId: customerId || undefined,
        customerName: customerName.trim() || undefined,
        customerCompany: customerCompany.trim() || undefined,
        customerPhone: customerPhone.trim() || undefined,
        customerEmail: customerEmail.trim() || undefined,
        customerGstNumber: customerGstNumber.trim() || undefined,
        customerCity: customerCity.trim() || undefined,
        customerNotes: customerNotes.trim() || undefined,
        vehicleId,
        pickupLocation,
        destination,
        startDate,
        endDate,
        amount,
        status,
      });
      onClose();
    } catch (err) {
      setError(getApiErrorMessage(err, 'Unable to save booking. Please try again.'));
    } finally {
      setSaving(false);
    }
  }

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-slate-950/40 px-4 py-6">
      <div className="w-full max-w-3xl rounded-3xl bg-white p-6 shadow-2xl shadow-slate-900/10">
        <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-xl font-semibold text-slate-900">{booking ? 'Edit booking' : 'Create new booking'}</h2>
            <p className="text-sm text-slate-500">Capture booking details inline, choose the vehicle, and set the travel dates.</p>
          </div>
          <Button type="button" variant="ghost" onClick={onClose}>
            Close
          </Button>
        </div>

        <form onSubmit={handleSubmit} className="grid gap-4 md:grid-cols-2">
          <label className="space-y-2 md:col-span-2">
            <span className="text-sm font-medium text-slate-700">Customer details (booking-first)</span>
            <p className="text-xs text-slate-500">You can save a booking without creating a separate customer record. Name or phone is enough.</p>
          </label>

          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Customer name</span>
            <Input value={customerName} onChange={(event) => setCustomerName(event.target.value)} placeholder="Guest / walk-in customer" />
          </label>

          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Phone</span>
            <Input value={customerPhone} onChange={(event) => setCustomerPhone(event.target.value)} placeholder="Mobile number" />
          </label>

          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Company</span>
            <Input value={customerCompany} onChange={(event) => setCustomerCompany(event.target.value)} placeholder="Optional company" />
          </label>

          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Email</span>
            <Input value={customerEmail} onChange={(event) => setCustomerEmail(event.target.value)} type="email" placeholder="Optional email" />
          </label>

          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">GST number</span>
            <Input value={customerGstNumber} onChange={(event) => setCustomerGstNumber(event.target.value)} placeholder="Optional GST" />
          </label>

          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">City</span>
            <Input value={customerCity} onChange={(event) => setCustomerCity(event.target.value)} placeholder="Optional city" />
          </label>

          <label className="space-y-2 md:col-span-2">
            <span className="text-sm font-medium text-slate-700">Notes</span>
            <Input value={customerNotes} onChange={(event) => setCustomerNotes(event.target.value)} placeholder="Notes for the booking" />
          </label>

          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Vehicle</span>
            <select
              className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 shadow-sm focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200"
              value={vehicleId}
              onChange={(event) => setVehicleId(event.target.value)}
              required
            >
              <option value="">Select vehicle</option>
              {availableVehicles.map((vehicle) => (
                <option key={vehicle.id} value={vehicle.id}>
                  {vehicle.licensePlate} — {vehicle.make} {vehicle.model}
                </option>
              ))}
            </select>
            {startDate && endDate && availableVehicles.length === 0 && (
              <p className="text-xs text-amber-700">No vehicles are available for the selected dates.</p>
            )}
          </label>

          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Pickup Location</span>
            <Input value={pickupLocation} onChange={(event) => setPickupLocation(event.target.value)} required />
          </label>

          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Destination</span>
            <Input value={destination} onChange={(event) => setDestination(event.target.value)} required />
          </label>

          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Start Date</span>
            <Input value={startDate} onChange={(event) => setStartDate(event.target.value)} type="date" required />
          </label>

          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">End Date</span>
            <Input value={endDate} onChange={(event) => setEndDate(event.target.value)} type="date" required />
          </label>

          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Booking Amount</span>
            <Input value={amount} onChange={(event) => setAmount(Number(event.target.value))} type="number" min={0} required />
          </label>

          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Status</span>
            <select
              className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 shadow-sm focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200"
              value={status}
              onChange={(event) => setStatus(event.target.value)}
              required
            >
              <option value="active">Active</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </label>

          {error && (
            <div className="md:col-span-2 rounded-3xl bg-red-50 px-4 py-3 text-sm text-red-700">
              {error}
            </div>
          )}

          <div className="md:col-span-2 flex flex-col gap-3 sm:flex-row sm:justify-end">
            <Button type="button" variant="secondary" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={saving}>
              {saving ? 'Saving...' : booking ? 'Update booking' : 'Create booking'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
