import { useEffect, useMemo, useState } from 'react';
import { Plus, Search, Edit3, Eye, Play, CheckCircle2, XCircle, Trash2 } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { TripForm } from '../components/trips/TripForm';
import { fetchTrips, createTrip, updateTrip, deleteTrip } from '../services/tripService';
import { fetchBookings } from '../services/bookingService';
import { fetchVehicles } from '../services/vehicleService';
import type { Trip, Booking, Vehicle } from '../types';

function formatDateTime(value: string) {
  return new Date(value).toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function statusClass(status: Trip['status']) {
  if (status === 'pending') return 'bg-slate-100 text-slate-700';
  if (status === 'ongoing') return 'bg-emerald-100 text-emerald-700';
  if (status === 'completed') return 'bg-sky-100 text-sky-700';
  if (status === 'cancelled') return 'bg-red-100 text-red-700';
  return 'bg-slate-100 text-slate-700';
}

function formatCurrency(value: number) {
  return `₹${value.toLocaleString()}`;
}

export function Trips() {
  const [trips, setTrips] = useState<Trip[]>([]);
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [formOpen, setFormOpen] = useState(false);
  const [activeTrip, setActiveTrip] = useState<Trip | undefined>(undefined);
  const [detailsTrip, setDetailsTrip] = useState<Trip | undefined>(undefined);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError('');
      try {
        const [tripsData, bookingsData, vehiclesData] = await Promise.all([
          fetchTrips(),
          fetchBookings(),
          fetchVehicles(),
        ]);
        setTrips(tripsData);
        setBookings(bookingsData);
        setVehicles(vehiclesData);
      } catch {
        setError('Unable to load trip data. Please try again.');
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

  const bookingMap = useMemo(() => new Map(bookings.map((booking) => [booking.id, booking])), [bookings]);
  const vehicleMap = useMemo(() => new Map(vehicles.map((vehicle) => [vehicle.id, vehicle])), [vehicles]);

  const tripsWithLabels = useMemo(
    () =>
      trips.map((trip) => ({
        ...trip,
        bookingLabel: bookingMap.get(trip.bookingId)
          ? `${bookingMap.get(trip.bookingId)?.pickupLocation} → ${bookingMap.get(trip.bookingId)?.destination}`
          : trip.bookingId,
        vehicleLabel: vehicleMap.get(bookingMap.get(trip.bookingId)?.vehicleId ?? trip.vehicleId)?.licensePlate ?? 'Unknown',
      })),
    [trips, bookingMap, vehicleMap],
  );

  const filteredTrips = useMemo(() => {
    const normalized = search.toLowerCase().trim();
    return tripsWithLabels.filter((trip) =>
      [trip.bookingLabel, trip.vehicleLabel, trip.status]
        .join(' ')
        .toLowerCase()
        .includes(normalized),
    );
  }, [tripsWithLabels, search]);

  const activeTripIds = useMemo(
    () => new Set(trips.filter((trip) => trip.status === 'ongoing').map((trip) => trip.bookingId)),
    [trips],
  );

  async function refresh() {
    setLoading(true);
    setError('');
    try {
      const [tripsData, bookingsData, vehiclesData] = await Promise.all([
        fetchTrips(),
        fetchBookings(),
        fetchVehicles(),
      ]);
      setTrips(tripsData);
      setBookings(bookingsData);
      setVehicles(vehiclesData);
    } catch {
      setError('Unable to refresh trip data.');
    } finally {
      setLoading(false);
    }
  }

  async function handleSaveTrip(payload: Omit<Trip, 'id' | 'distanceKm'>) {
    if (activeTrip) {
      await updateTrip(activeTrip.id, payload);
    } else {
      await createTrip(payload);
    }
    await refresh();
  }

  async function handleStartTrip(tripId: string) {
    const trip = trips.find((item) => item.id === tripId);
    if (!trip || trip.status === 'cancelled' || trip.status === 'completed') return;
    if (activeTripIds.has(trip.bookingId) && trip.status !== 'ongoing') {
      setError('This booking already has an ongoing trip.');
      return;
    }
    setLoading(true);
    setError('');
    try {
      await updateTrip(tripId, { status: 'ongoing' });
      await refresh();
    } catch {
      setError('Unable to start the trip.');
      setLoading(false);
    }
  }

  async function handleCompleteTrip(tripId: string) {
    const trip = trips.find((item) => item.id === tripId);
    if (!trip || trip.status === 'cancelled' || trip.status === 'completed') return;
    setLoading(true);
    setError('');
    try {
      await updateTrip(tripId, { status: 'completed' });
      await refresh();
    } catch {
      setError('Unable to complete the trip.');
      setLoading(false);
    }
  }

  async function handleCancelTrip(tripId: string) {
    const confirmed = window.confirm('Cancel this trip?');
    if (!confirmed) return;
    setLoading(true);
    setError('');
    try {
      await updateTrip(tripId, { status: 'cancelled' });
      await refresh();
    } catch {
      setError('Unable to cancel the trip.');
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="rounded-3xl bg-white p-6 shadow-sm shadow-slate-200/80 sm:flex sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Trips</h1>
          <p className="mt-1 text-sm text-slate-600">Track fleet trips from booking to completion.</p>
        </div>
        <div className="mt-4 flex flex-col gap-3 sm:mt-0 sm:flex-row sm:items-center">
          <Button
            onClick={() => {
              setActiveTrip(undefined);
              setFormOpen(true);
            }}
          >
            <Plus className="mr-2 h-4 w-4" />
            Create trip
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
            <Input className="pl-11" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search trips" />
          </div>
          <p className="text-sm text-slate-500">
            {loading ? 'Loading trips…' : `${filteredTrips.length} trip${filteredTrips.length === 1 ? '' : 's'}`}
          </p>
        </div>

        {error && (
          <div className="mb-6 rounded-3xl bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
        )}

        {loading ? (
          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-10 text-center text-slate-500">Loading trips...</div>
        ) : filteredTrips.length === 0 ? (
          <div className="rounded-3xl border border-dashed border-slate-200 bg-slate-50 p-10 text-center text-slate-500">
            <p className="mb-3 text-lg font-semibold text-slate-900">No trips found</p>
            <p>Use the Create trip button to begin tracking fleet activity.</p>
          </div>
        ) : (
          <div className="overflow-hidden rounded-3xl border border-slate-200">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
                <thead className="bg-slate-50 text-slate-600">
                  <tr>
                    <th className="px-6 py-4 font-medium">Booking</th>
                    <th className="px-6 py-4 font-medium">Vehicle</th>
                    <th className="px-6 py-4 font-medium">Start KM</th>
                    <th className="px-6 py-4 font-medium">End KM</th>
                    <th className="px-6 py-4 font-medium">Distance</th>
                    <th className="px-6 py-4 font-medium">Revenue</th>
                    <th className="px-6 py-4 font-medium">Start Time</th>
                    <th className="px-6 py-4 font-medium">End Time</th>
                    <th className="px-6 py-4 font-medium">Status</th>
                    <th className="px-6 py-4 font-medium text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 bg-white">
                  {filteredTrips.map((trip) => (
                    <tr key={trip.id} className="hover:bg-slate-50">
                      <td className="px-6 py-4 font-medium text-slate-900">{trip.bookingLabel}</td>
                      <td className="px-6 py-4 text-slate-600">{trip.vehicleLabel}</td>
                      <td className="px-6 py-4 text-slate-600">{trip.startKm}</td>
                      <td className="px-6 py-4 text-slate-600">{trip.endKm}</td>
                      <td className="px-6 py-4 text-slate-600">{trip.distanceKm} km</td>
                      <td className="px-6 py-4 text-slate-600">{formatCurrency(trip.revenue)}</td>
                      <td className="px-6 py-4 text-slate-600">{formatDateTime(trip.startTime)}</td>
                      <td className="px-6 py-4 text-slate-600">{formatDateTime(trip.endTime)}</td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${statusClass(trip.status)}`}>
                          {trip.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="inline-flex flex-wrap items-center justify-end gap-2">
                          <Button
                            type="button"
                            variant="secondary"
                            className="inline-flex items-center gap-2"
                            onClick={() => setDetailsTrip(trip)}
                          >
                            <Eye className="h-4 w-4" />
                            View
                          </Button>
                          <Button
                            type="button"
                            variant="secondary"
                            className="inline-flex items-center gap-2"
                            onClick={() => {
                              setActiveTrip(trip);
                              setFormOpen(true);
                            }}
                          >
                            <Edit3 className="h-4 w-4" />
                            Edit
                          </Button>
                          {trip.status !== 'cancelled' && trip.status !== 'completed' && (
                            <>
                              {trip.status === 'pending' && (
                                <Button
                                  type="button"
                                  variant="ghost"
                                  className="inline-flex items-center gap-2 text-emerald-600 hover:bg-emerald-50"
                                  onClick={() => handleStartTrip(trip.id)}
                                >
                                  <Play className="h-4 w-4" />
                                  Start
                                </Button>
                              )}
                              <Button
                                type="button"
                                variant="ghost"
                                className="inline-flex items-center gap-2 text-sky-600 hover:bg-sky-50"
                                onClick={() => handleCompleteTrip(trip.id)}
                              >
                                <CheckCircle2 className="h-4 w-4" />
                                Complete
                              </Button>
                              <Button
                                type="button"
                                variant="ghost"
                                className="inline-flex items-center gap-2 text-red-600 hover:bg-red-50"
                                onClick={() => handleCancelTrip(trip.id)}
                              >
                                <XCircle className="h-4 w-4" />
                                Cancel
                              </Button>
                            </>
                          )}
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

      <TripForm
        open={formOpen}
        trip={activeTrip}
        bookings={bookings}
        vehicles={vehicles}
        trips={trips}
        onClose={() => setFormOpen(false)}
        onSave={handleSaveTrip}
      />

      {detailsTrip && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/40 px-4 py-6">
          <div className="w-full max-w-2xl rounded-3xl bg-white p-6 shadow-2xl shadow-slate-900/10">
            <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 className="text-xl font-semibold text-slate-900">Trip details</h2>
                <p className="text-sm text-slate-500">Review trip status, distance, and schedule.</p>
              </div>
              <Button type="button" variant="ghost" onClick={() => setDetailsTrip(undefined)}>
                Close
              </Button>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-sm text-slate-500">Booking</p>
                <p className="mt-2 font-semibold text-slate-900">
                  {bookingMap.get(detailsTrip.bookingId)
                    ? `${bookingMap.get(detailsTrip.bookingId)?.pickupLocation} → ${bookingMap.get(detailsTrip.bookingId)?.destination}`
                    : detailsTrip.bookingId}
                </p>
              </div>
              <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-sm text-slate-500">Vehicle</p>
                <p className="mt-2 font-semibold text-slate-900">
                  {vehicleMap.get(bookingMap.get(detailsTrip.bookingId)?.vehicleId ?? detailsTrip.bookingId)?.licensePlate ?? 'Unknown'}
                </p>
              </div>
              <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-sm text-slate-500">Start / End KM</p>
                <p className="mt-2 font-semibold text-slate-900">{detailsTrip.startKm} → {detailsTrip.endKm}</p>
              </div>
              <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-sm text-slate-500">Distance</p>
                <p className="mt-2 font-semibold text-slate-900">{detailsTrip.distanceKm} km</p>
              </div>
              <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-sm text-slate-500">Start time</p>
                <p className="mt-2 font-semibold text-slate-900">{formatDateTime(detailsTrip.startTime)}</p>
              </div>
              <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-sm text-slate-500">End time</p>
                <p className="mt-2 font-semibold text-slate-900">{formatDateTime(detailsTrip.endTime)}</p>
              </div>
              <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4 sm:col-span-2">
                <p className="text-sm text-slate-500">Revenue</p>
                <p className="mt-2 font-semibold text-slate-900">{formatCurrency(detailsTrip.revenue)}</p>
              </div>
              <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4 sm:col-span-2">
                <p className="text-sm text-slate-500">Status</p>
                <span className={`mt-2 inline-flex rounded-full px-3 py-1 text-xs font-semibold ${statusClass(detailsTrip.status)}`}>
                  {detailsTrip.status}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
