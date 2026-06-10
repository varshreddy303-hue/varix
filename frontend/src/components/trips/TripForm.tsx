import { useEffect, useMemo, useState } from 'react';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { getApiErrorMessage } from '../../lib/api';
import type { Booking, Trip, Vehicle } from '../../types';

interface TripFormProps {
  open: boolean;
  trip?: Trip;
  bookings: Booking[];
  vehicles: Vehicle[];
  trips: Trip[];
  onClose: () => void;
  onSave: (payload: Omit<Trip, 'id' | 'distanceKm'>) => Promise<void>;
}

function overlap(startA: string, endA: string, startB: string, endB: string) {
  return !(new Date(endA) < new Date(startB) || new Date(startA) > new Date(endB));
}

export function TripForm({ open, trip, bookings, vehicles, trips, onClose, onSave }: TripFormProps) {
  const [bookingId, setBookingId] = useState('');
  const [startKm, setStartKm] = useState(0);
  const [endKm, setEndKm] = useState(0);
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');
  const [revenue, setRevenue] = useState(0);
  const [status, setStatus] = useState<Trip['status']>('pending');
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (trip) {
      setBookingId(trip.bookingId);
      setStartKm(trip.startKm);
      setEndKm(trip.endKm);
      setStartTime(trip.startTime);
      setEndTime(trip.endTime);
      setRevenue(trip.revenue);
      setStatus(trip.status);
      setError('');
    } else {
      setBookingId(bookings[0]?.id ?? '');
      setStartKm(0);
      setEndKm(0);
      setStartTime('');
      setEndTime('');
      setRevenue(0);
      setStatus('pending');
      setError('');
    }
  }, [trip, open, bookings]);

  const activeBookingTripIds = useMemo(
    () => new Set(trips.filter((item) => item.status === 'ongoing' && item.bookingId !== trip?.bookingId).map((item) => item.bookingId)),
    [trips, trip],
  );

  const availableBookings = useMemo(() => {
    return bookings.filter((booking) => !activeBookingTripIds.has(booking.id) || booking.id === trip?.bookingId);
  }, [bookings, activeBookingTripIds, trip]);

  const bookingVehicle = useMemo(() => {
    const activeBooking = bookings.find((item) => item.id === bookingId);
    return vehicles.find((vehicle) => vehicle.id === activeBooking?.vehicleId);
  }, [bookingId, bookings, vehicles]);

  const distance = Math.max(0, endKm - startKm);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError('');
    setSaving(true);

    if (!bookingId || !startTime || !endTime || revenue < 0) {
      setError('Please complete all required fields.');
      setSaving(false);
      return;
    }

    if (!bookingVehicle) {
      setError('Selected booking does not have an assigned vehicle.');
      setSaving(false);
      return;
    }

    if (new Date(endTime) < new Date(startTime)) {
      setError('End time must be after start time.');
      setSaving(false);
      return;
    }

    if (endKm < startKm) {
      setError('End KM must be greater than or equal to start KM.');
      setSaving(false);
      return;
    }

    if (status === 'ongoing' && bookingId && activeBookingTripIds.has(bookingId) && bookingId !== trip?.bookingId) {
      setError('Selected booking already has an ongoing trip.');
      setSaving(false);
      return;
    }

    try {
      await onSave({
        bookingId,
        vehicleId: bookingVehicle.id,
        startKm,
        endKm,
        revenue,
        startTime,
        endTime,
        status,
      });
      onClose();
    } catch (err) {
      setError(getApiErrorMessage(err, 'Unable to save this trip.'));
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
            <h2 className="text-xl font-semibold text-slate-900">{trip ? 'Edit trip' : 'Create trip'}</h2>
            <p className="text-sm text-slate-500">Assign a booking, track kilometres, and capture trip status.</p>
          </div>
          <Button type="button" variant="ghost" onClick={onClose}>
            Close
          </Button>
        </div>

        <form onSubmit={handleSubmit} className="grid gap-4 md:grid-cols-2">
          <label className="space-y-2 md:col-span-2">
            <span className="text-sm font-medium text-slate-700">Booking</span>
            <select
              className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 shadow-sm focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200"
              value={bookingId}
              onChange={(event) => setBookingId(event.target.value)}
              required
            >
              <option value="">Select booking</option>
              {availableBookings.map((booking) => (
                <option key={booking.id} value={booking.id}>
                  {booking.id} — {booking.pickupLocation} to {booking.destination}
                </option>
              ))}
            </select>
            {bookingVehicle && (
              <p className="text-sm text-slate-500">Vehicle: {bookingVehicle.licensePlate} ({bookingVehicle.make} {bookingVehicle.model})</p>
            )}
          </label>

          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Start KM</span>
            <Input value={startKm} onChange={(event) => setStartKm(Number(event.target.value))} type="number" min={0} required />
          </label>

          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">End KM</span>
            <Input value={endKm} onChange={(event) => setEndKm(Number(event.target.value))} type="number" min={0} required />
          </label>

          <div className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Distance</span>
            <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-700">{distance} km</div>
          </div>

          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Revenue</span>
            <Input value={revenue} onChange={(event) => setRevenue(Number(event.target.value))} type="number" min={0} required />
          </label>

          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Start Time</span>
            <Input value={startTime} onChange={(event) => setStartTime(event.target.value)} type="datetime-local" required />
          </label>

          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">End Time</span>
            <Input value={endTime} onChange={(event) => setEndTime(event.target.value)} type="datetime-local" required />
          </label>

          <label className="space-y-2 md:col-span-2">
            <span className="text-sm font-medium text-slate-700">Status</span>
            <select
              className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 shadow-sm focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200"
              value={status}
              onChange={(event) => setStatus(event.target.value as Trip['status'])}
              required
            >
              <option value="pending">Pending</option>
              <option value="ongoing">Ongoing</option>
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
              {saving ? 'Saving...' : trip ? 'Update trip' : 'Create trip'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
