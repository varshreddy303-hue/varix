import { useEffect, useMemo, useState } from 'react';
import { Plus, Search, Filter, Edit3, Trash2, Eye } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { ExpenseForm } from '../components/expenses/ExpenseForm';
import { fetchExpenses, createExpense, updateExpense, deleteExpense } from '../services/expenseService';
import { fetchBookings } from '../services/bookingService';
import { fetchTrips } from '../services/tripService';
import { fetchVehicles } from '../services/vehicleService';
import type { Booking, Expense, Trip, Vehicle } from '../types';

function formatDate(value: string) {
  return new Date(value).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
}

function formatCurrency(value: number) {
  return `₹${value.toLocaleString()}`;
}

export function Expenses() {
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [trips, setTrips] = useState<Trip[]>([]);
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [search, setSearch] = useState('');
  const [vehicleFilter, setVehicleFilter] = useState('All');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [formOpen, setFormOpen] = useState(false);
  const [activeExpense, setActiveExpense] = useState<Expense | undefined>(undefined);
  const [detailsExpense, setDetailsExpense] = useState<Expense | undefined>(undefined);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError('');
      try {
        const [expensesData, tripsData, bookingsData, vehiclesData] = await Promise.all([
          fetchExpenses(),
          fetchTrips(),
          fetchBookings(),
          fetchVehicles(),
        ]);
        setExpenses(expensesData);
        setTrips(tripsData);
        setBookings(bookingsData);
        setVehicles(vehiclesData);
      } catch {
        setError('Unable to load expenses. Please try again.');
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

  const tripMap = useMemo(() => new Map(trips.map((trip) => [trip.id, trip])), [trips]);
  const vehicleMap = useMemo(() => new Map(vehicles.map((vehicle) => [vehicle.id, vehicle])), [vehicles]);

  const expensesWithLabels = useMemo(
    () =>
      expenses.map((expense) => ({
        ...expense,
        tripLabel: tripMap.get(expense.tripId)
          ? `Trip ${tripMap.get(expense.tripId)?.id}`
          : expense.tripId,
        vehicleLabel: vehicleMap.get(expense.vehicleId)?.licensePlate ?? 'Unknown',
      })),
    [expenses, tripMap, vehicleMap],
  );

  const filteredExpenses = useMemo(() => {
    const normalized = search.toLowerCase().trim();
    return expensesWithLabels.filter((expense) => {
      const matchesText = [expense.tripLabel, expense.vehicleLabel]
        .join(' ')
        .toLowerCase()
        .includes(normalized);

      const matchesVehicle = vehicleFilter === 'All' || expense.vehicleId === vehicleFilter;
      const matchesDate = (() => {
        if (!startDate && !endDate) return true;
        const expenseTime = new Date(expense.expenseDate).getTime();
        if (startDate && expenseTime < new Date(startDate).getTime()) return false;
        if (endDate && expenseTime > new Date(endDate).getTime()) return false;
        return true;
      })();

      return matchesText && matchesVehicle && matchesDate;
    });
  }, [expensesWithLabels, search, vehicleFilter, startDate, endDate]);

  async function refresh() {
    setLoading(true);
    setError('');
    try {
      const [expensesData, tripsData, bookingsData, vehiclesData] = await Promise.all([
        fetchExpenses(),
        fetchTrips(),
        fetchBookings(),
        fetchVehicles(),
      ]);
      setExpenses(expensesData);
      setTrips(tripsData);
      setBookings(bookingsData);
      setVehicles(vehiclesData);
    } catch {
      setError('Unable to refresh expenses.');
    } finally {
      setLoading(false);
    }
  }

  async function handleSaveExpense(payload: Omit<Expense, 'id'>) {
    if (activeExpense) {
      await updateExpense(activeExpense.id, payload);
    } else {
      await createExpense(payload);
    }
    await refresh();
  }

  async function handleDeleteExpense(expenseId: string) {
    const confirmed = window.confirm('Delete this expense?');
    if (!confirmed) return;
    setLoading(true);
    setError('');
    try {
      await deleteExpense(expenseId);
      await refresh();
    } catch {
      setError('Unable to delete expense.');
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="rounded-3xl bg-white p-6 shadow-sm shadow-slate-200/80 sm:flex sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Expenses</h1>
          <p className="mt-1 text-sm text-slate-600">Track trip expenses, filter by category, and review vehicle costs.</p>
        </div>
        <div className="mt-4 flex flex-col gap-3 sm:mt-0 sm:flex-row sm:items-center">
          <Button
            onClick={() => {
              setActiveExpense(undefined);
              setFormOpen(true);
            }}
          >
            <Plus className="mr-2 h-4 w-4" />
            Add expense
          </Button>
          <Button variant="secondary" onClick={refresh} disabled={loading}>
            Refresh
          </Button>
        </div>
      </div>

      <Card>
        <div className="mb-6 grid gap-4 lg:grid-cols-[1fr_auto] lg:items-end">
          <div className="relative max-w-md">
            <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <Input className="pl-11" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search expenses" />
          </div>
          <div className="flex items-center gap-3">
            <Filter className="h-4 w-4 text-slate-400" />
            <select
              className="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 shadow-sm focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200"
              value={vehicleFilter}
              onChange={(event) => setVehicleFilter(event.target.value)}
            >
              <option value="All">All vehicles</option>
              {vehicles.map((vehicle) => (
                <option key={vehicle.id} value={vehicle.id}>
                  {vehicle.licensePlate}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="mb-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Start Date</span>
            <Input value={startDate} onChange={(event) => setStartDate(event.target.value)} type="date" />
          </label>
          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">End Date</span>
            <Input value={endDate} onChange={(event) => setEndDate(event.target.value)} type="date" />
          </label>
          <div className="flex items-end">
            <Button variant="secondary" onClick={() => { setStartDate(''); setEndDate(''); }}>
              Clear dates
            </Button>
          </div>
        </div>

        {error && (
          <div className="mb-6 rounded-3xl bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
        )}

        {loading ? (
          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-10 text-center text-slate-500">Loading expenses...</div>
        ) : filteredExpenses.length === 0 ? (
          <div className="rounded-3xl border border-dashed border-slate-200 bg-slate-50 p-10 text-center text-slate-500">
            <p className="mb-3 text-lg font-semibold text-slate-900">No expenses found</p>
            <p>Record your first expense with the Add expense button.</p>
          </div>
        ) : (
          <div className="overflow-hidden rounded-3xl border border-slate-200">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
                <thead className="bg-slate-50 text-slate-600">
                  <tr>
                    <th className="px-6 py-4 font-medium">Trip</th>
                    <th className="px-6 py-4 font-medium">Vehicle</th>
                    <th className="px-6 py-4 font-medium">Total</th>
                    <th className="px-6 py-4 font-medium">Expense Date</th>
                    <th className="px-6 py-4 font-medium text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 bg-white">
                  {filteredExpenses.map((expense) => (
                    <tr key={expense.id} className="hover:bg-slate-50">
                      <td className="px-6 py-4 font-medium text-slate-900">{expense.tripLabel}</td>
                      <td className="px-6 py-4 text-slate-600">{expense.vehicleLabel}</td>
                      <td className="px-6 py-4 text-slate-600">{formatCurrency(expense.totalAmount)}</td>
                      <td className="px-6 py-4 text-slate-600">{formatDate(expense.expenseDate)}</td>
                      <td className="px-6 py-4 text-right">
                        <div className="inline-flex flex-wrap items-center justify-end gap-2">
                          <Button type="button" variant="secondary" className="inline-flex items-center gap-2" onClick={() => setDetailsExpense(expense)}>
                            <Eye className="h-4 w-4" />
                            View
                          </Button>
                          <Button type="button" variant="secondary" className="inline-flex items-center gap-2" onClick={() => { setActiveExpense(expense); setFormOpen(true); }}>
                            <Edit3 className="h-4 w-4" />
                            Edit
                          </Button>
                          <Button type="button" variant="ghost" className="inline-flex items-center gap-2 text-red-600 hover:bg-red-50" onClick={() => handleDeleteExpense(expense.id)}>
                            <Trash2 className="h-4 w-4" />
                            Delete
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

      <ExpenseForm
        open={formOpen}
        expense={activeExpense}
        trips={trips}
        bookings={bookings}
        vehicles={vehicles}
        onClose={() => setFormOpen(false)}
        onSave={handleSaveExpense}
      />

      {detailsExpense && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/40 px-4 py-6">
          <div className="w-full max-w-2xl rounded-3xl bg-white p-6 shadow-2xl shadow-slate-900/10">
            <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 className="text-xl font-semibold text-slate-900">Expense details</h2>
                <p className="text-sm text-slate-500">Review the expense record for this trip and vehicle.</p>
              </div>
              <Button type="button" variant="ghost" onClick={() => setDetailsExpense(undefined)}>
                Close
              </Button>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-sm text-slate-500">Trip</p>
                <p className="mt-2 font-semibold text-slate-900">
                  {tripMap.get(detailsExpense.tripId)
                    ? `Trip ${tripMap.get(detailsExpense.tripId)?.id}`
                    : detailsExpense.tripId}
                </p>
              </div>
              <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-sm text-slate-500">Vehicle</p>
                <p className="mt-2 font-semibold text-slate-900">{vehicleMap.get(detailsExpense.vehicleId)?.licensePlate ?? 'Unknown'}</p>
              </div>
              <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-sm text-slate-500">Total</p>
                <p className="mt-2 font-semibold text-slate-900">{formatCurrency(detailsExpense.totalAmount)}</p>
              </div>
              <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4 sm:col-span-2">
                <p className="text-sm text-slate-500">Expense components</p>
                <div className="mt-2 space-y-2 text-slate-900">
                  <p>Fuel: {formatCurrency(detailsExpense.fuelAmount)}</p>
                  <p>Toll: {formatCurrency(detailsExpense.tollAmount)}</p>
                  <p>Parking: {formatCurrency(detailsExpense.parkingAmount)}</p>
                  <p>Driver bata: {formatCurrency(detailsExpense.driverBataAmount)}</p>
                  <p>Permit: {formatCurrency(detailsExpense.permitAmount)}</p>
                  <p>State tax: {formatCurrency(detailsExpense.stateTaxAmount)}</p>
                  <p>Food: {formatCurrency(detailsExpense.foodAmount)}</p>
                  <p>Accommodation: {formatCurrency(detailsExpense.accommodationAmount)}</p>
                  <p>Misc: {formatCurrency(detailsExpense.miscAmount)}</p>
                </div>
              </div>
              <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4 sm:col-span-2">
                <p className="text-sm text-slate-500">Expense Date</p>
                <p className="mt-2 font-semibold text-slate-900">{formatDate(detailsExpense.expenseDate)}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
