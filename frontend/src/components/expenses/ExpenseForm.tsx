import { useEffect, useMemo, useState } from 'react';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { getApiErrorMessage } from '../../lib/api';
import type { Booking, Expense, Trip, Vehicle } from '../../types';

interface StateTaxRow {
  id: number;
  state: string;
  amount: number;
}

interface ExpenseFormProps {
  open: boolean;
  expense?: Expense;
  trips: Trip[];
  bookings: Booking[];
  vehicles: Vehicle[];
  onClose: () => void;
  onSave: (payload: Omit<Expense, 'id'>) => Promise<void>;
}

export function ExpenseForm({ open, expense, trips, bookings, vehicles, onClose, onSave }: ExpenseFormProps) {
  const [tripId, setTripId] = useState('');
  const [bookingId, setBookingId] = useState('');
  const [startKm, setStartKm] = useState(0);
  const [endKm, setEndKm] = useState(0);
  const [kmRate, setKmRate] = useState(0);
  const [driverBataAmount, setDriverBataAmount] = useState(0);
  const [tollAmount, setTollAmount] = useState(0);
  const [parkingAmount, setParkingAmount] = useState(0);
  const [miscAmount, setMiscAmount] = useState(0);
  const [stateTaxRows, setStateTaxRows] = useState<StateTaxRow[]>([]);
  const [expenseDate, setExpenseDate] = useState(() => new Date().toISOString().slice(0, 10));
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (expense) {
      setTripId(expense.tripId ?? '');
      setBookingId(expense.bookingId ?? '');
      setStartKm(0);
      setEndKm(0);
      setKmRate(0);
      setDriverBataAmount(expense.driverBataAmount);
      setTollAmount(expense.tollAmount);
      setParkingAmount(expense.parkingAmount);
      setMiscAmount(expense.miscAmount);
      setStateTaxRows([{ id: Date.now(), state: 'State Tax', amount: expense.stateTaxAmount }]);
      setExpenseDate(expense.expenseDate.slice(0, 10));
      setError('');
    } else {
      setTripId('');
      setBookingId('');
      setStartKm(0);
      setEndKm(0);
      setKmRate(0);
      setDriverBataAmount(0);
      setTollAmount(0);
      setParkingAmount(0);
      setMiscAmount(0);
      setStateTaxRows([]);
      setExpenseDate(new Date().toISOString().slice(0, 10));
      setError('');
    }
  }, [expense, open]);

  const selectedBooking = useMemo(
    () => bookings.find((booking) => booking.id === bookingId),
    [bookingId, bookings],
  );

  const selectedTrip = useMemo(() => {
    if (expense && expense.tripId) {
      return trips.find((trip) => trip.id === expense.tripId);
    }
    return trips.find((trip) => trip.bookingId === bookingId);
  }, [bookingId, expense, trips]);

  const selectedVehicle = useMemo(
    () => vehicles.find((vehicle) => vehicle.id === selectedBooking?.vehicleId || selectedTrip?.vehicleId),
    [selectedBooking, selectedTrip, vehicles],
  );

  const totalKm = Math.max(0, endKm - startKm);
  const tripAmount = totalKm * kmRate;
  const stateTaxAmount = stateTaxRows.reduce((sum, row) => sum + row.amount, 0);
  const totalAmount = tripAmount + driverBataAmount + tollAmount + parkingAmount + stateTaxAmount + miscAmount;

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError('');
    setSaving(true);

    const targetTripId = expense?.tripId ?? selectedTrip?.id;
    if (!targetTripId) {
      setError('Please select a booking with an assigned trip.');
      setSaving(false);
      return;
    }

    if (endKm < startKm) {
      setError('End KM must be greater than or equal to Start KM.');
      setSaving(false);
      return;
    }

    if (totalAmount <= 0) {
      setError('Grand total must be greater than zero.');
      setSaving(false);
      return;
    }

    if (!selectedVehicle) {
      setError('Unable to determine the vehicle for this expense.');
      setSaving(false);
      return;
    }

    try {
      await onSave({
        tripId: targetTripId,
        vehicleId: selectedVehicle.id,
        amount: tripAmount,
        fuelAmount: 0,
        tollAmount,
        parkingAmount,
        driverBataAmount,
        permitAmount: 0,
        stateTaxAmount,
        foodAmount: 0,
        accommodationAmount: 0,
        miscAmount,
        totalAmount,
        expenseDate,
      });
      onClose();
    } catch (err) {
      setError(getApiErrorMessage(err, 'Unable to save expense. Please try again.'));
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
            <h2 className="text-xl font-semibold text-slate-900">{expense ? 'Edit expense' : 'Add trip expense'}</h2>
            <p className="text-sm text-slate-500">Enter customer and vehicle trip details once, then save the expense with automatic totals.</p>
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
            >
              <option value="">Select booking</option>
              {bookings.map((booking) => (
                <option key={booking.id} value={booking.id}>
                  Booking {booking.id} • {booking.startDate.slice(0, 10)} → {booking.endDate.slice(0, 10)}
                </option>
              ))}
            </select>
          </label>

          <div className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Customer</span>
            <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900">
              {selectedBooking ? `Booking ${selectedBooking.id}` : 'Select booking to show customer'}
            </div>
          </div>

          <div className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Vehicle Number</span>
            <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900">
              {selectedVehicle ? selectedVehicle.licensePlate : 'Select booking to show vehicle'}
            </div>
          </div>

          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Start KM Reading</span>
            <Input type="number" min={0} step="1" value={startKm} onChange={(event) => setStartKm(Number(event.target.value) || 0)} required />
          </label>

          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">End KM Reading</span>
            <Input type="number" min={0} step="1" value={endKm} onChange={(event) => setEndKm(Number(event.target.value) || 0)} required />
          </label>

          <div className="space-y-2 md:col-span-2">
            <span className="text-sm font-medium text-slate-700">Total KM</span>
            <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900">{totalKm} km</div>
          </div>

          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">KM Rate</span>
            <Input type="number" min={0} step="0.01" value={kmRate} onChange={(event) => setKmRate(Number(event.target.value) || 0)} required />
          </label>

          <div className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Trip Amount</span>
            <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900">₹{tripAmount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
          </div>

          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Driver Bata</span>
            <Input type="number" min={0} step="0.01" value={driverBataAmount} onChange={(event) => setDriverBataAmount(Number(event.target.value) || 0)} />
          </label>

          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Toll Amount</span>
            <Input type="number" min={0} step="0.01" value={tollAmount} onChange={(event) => setTollAmount(Number(event.target.value) || 0)} />
          </label>

          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Parking Amount</span>
            <Input type="number" min={0} step="0.01" value={parkingAmount} onChange={(event) => setParkingAmount(Number(event.target.value) || 0)} />
          </label>

          <div className="md:col-span-2 rounded-3xl border border-slate-200 bg-slate-50 p-4">
            <div className="mb-4 flex items-center justify-between gap-4">
              <div>
                <p className="text-sm font-medium text-slate-700">State Tax</p>
                <p className="text-sm text-slate-500">Add each tax row separately.</p>
              </div>
              <Button
                type="button"
                variant="secondary"
                onClick={() => setStateTaxRows((current) => [...current, { id: Date.now(), state: '', amount: 0 }])}
              >
                Add State Tax
              </Button>
            </div>
            <div className="space-y-3">
              {stateTaxRows.map((row) => (
                <div key={row.id} className="grid gap-3 sm:grid-cols-[1fr_auto]">
                  <label className="space-y-2">
                    <span className="text-sm font-medium text-slate-700">State</span>
                    <Input
                      value={row.state}
                      onChange={(event) =>
                        setStateTaxRows((current) =>
                          current.map((item) => (item.id === row.id ? { ...item, state: event.target.value } : item)),
                        )
                      }
                      placeholder="Telangana"
                    />
                  </label>
                  <div className="grid gap-2">
                    <label className="space-y-2">
                      <span className="text-sm font-medium text-slate-700">Amount</span>
                      <Input
                        type="number"
                        min={0}
                        step="0.01"
                        value={row.amount}
                        onChange={(event) =>
                          setStateTaxRows((current) =>
                            current.map((item) =>
                              item.id === row.id ? { ...item, amount: Number(event.target.value) || 0 } : item,
                            ),
                          )
                        }
                      />
                    </label>
                    <Button
                      type="button"
                      variant="ghost"
                      onClick={() => setStateTaxRows((current) => current.filter((item) => item.id !== row.id))}
                    >
                      Remove
                    </Button>
                  </div>
                </div>
              ))}
              {stateTaxRows.length === 0 && <p className="text-sm text-slate-500">No state tax rows yet.</p>}
            </div>
          </div>

          <label className="space-y-2 md:col-span-2">
            <span className="text-sm font-medium text-slate-700">Miscellaneous Amount</span>
            <Input type="number" min={0} step="0.01" value={miscAmount} onChange={(event) => setMiscAmount(Number(event.target.value) || 0)} />
          </label>

          <label className="space-y-2 md:col-span-2">
            <span className="text-sm font-medium text-slate-700">Expense Date</span>
            <Input value={expenseDate} onChange={(event) => setExpenseDate(event.target.value)} type="date" required />
          </label>

          <div className="space-y-2 md:col-span-2">
            <span className="text-sm font-medium text-slate-700">Grand Total</span>
            <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900">
              ₹{totalAmount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
          </div>

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
              {saving ? 'Saving...' : expense ? 'Update expense' : 'Save expense'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
