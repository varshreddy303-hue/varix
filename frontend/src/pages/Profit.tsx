import { useEffect, useMemo, useState } from 'react';
import { Card } from '../components/ui/Card';
import { ProfitFilters } from '../components/profit/ProfitFilters';
import { ProfitSummaryCards } from '../components/profit/ProfitSummaryCards';
import { ProfitTable } from '../components/profit/ProfitTable';
import { fetchProfitSummary, fetchTripProfit, fetchVehicleDailyProfit, fetchVehicleMonthlyProfit } from '../services/profitService';
import { fetchTrips } from '../services/tripService';
import { fetchVehicles } from '../services/vehicleService';
import type { ProfitSummary, Trip, Vehicle, TripProfit, VehicleDailyProfit, VehicleMonthlyProfit } from '../types';

function formatCurrency(value: number) {
  return `₹${value.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
}

function formatDate(value: string) {
  return new Date(value).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
}

function formatMonth(year: number, month: number) {
  return new Date(year, month - 1, 1).toLocaleDateString(undefined, { month: 'short', year: 'numeric' });
}

export function Profit() {
  const [summary, setSummary] = useState<ProfitSummary | null>(null);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [trips, setTrips] = useState<Trip[]>([]);
  const [tripProfits, setTripProfits] = useState<TripProfit[]>([]);
  const [dailyProfits, setDailyProfits] = useState<VehicleDailyProfit[]>([]);
  const [monthlyProfits, setMonthlyProfits] = useState<VehicleMonthlyProfit[]>([]);
  const [selectedVehicleId, setSelectedVehicleId] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [selectedMonth, setSelectedMonth] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  async function loadVehicleProfit(vehicleId: string, shouldShowLoading = true) {
    if (!vehicleId) return;
    if (shouldShowLoading) {
      setLoading(true);
      setError('');
    }

    try {
      const [dailyResponse, monthlyResponse] = await Promise.all([
        fetchVehicleDailyProfit(vehicleId, { page: 1, page_size: 200 }),
        fetchVehicleMonthlyProfit(vehicleId, { page: 1, page_size: 200 }),
      ]);
      setDailyProfits(dailyResponse);
      setMonthlyProfits(monthlyResponse);
    } catch {
      setError('Unable to load vehicle profit details.');
    } finally {
      if (shouldShowLoading) {
        setLoading(false);
      }
    }
  }

  async function loadProfitData() {
    setLoading(true);
    setError('');

    try {
      const [summaryResponse, vehiclesResponse, tripsResponse] = await Promise.all([
        fetchProfitSummary(),
        fetchVehicles(),
        fetchTrips(),
      ]);

      setSummary(summaryResponse);
      setVehicles(vehiclesResponse);
      setTrips(tripsResponse);

      const defaultVehicle = selectedVehicleId || vehiclesResponse[0]?.id || '';
      if (defaultVehicle) {
        setSelectedVehicleId(defaultVehicle);
      }

      const profitResponses: TripProfit[] = await Promise.all(
        tripsResponse.map((trip: Trip) => fetchTripProfit(trip.id)),
      );
      setTripProfits(profitResponses);

      if (defaultVehicle) {
        await loadVehicleProfit(defaultVehicle, false);
      }
    } catch {
      setError('Unable to load profit data. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadProfitData();
  }, []);

  useEffect(() => {
    if (selectedVehicleId) {
      loadVehicleProfit(selectedVehicleId);
    }
  }, [selectedVehicleId]);

  useEffect(() => {
    if (!selectedVehicleId && vehicles.length > 0) {
      setSelectedVehicleId(vehicles[0].id);
    }
  }, [vehicles, selectedVehicleId]);

  const vehicleMap = useMemo(
    () => new Map<string, Vehicle>(vehicles.map((vehicle: Vehicle) => [vehicle.id, vehicle])),
    [vehicles],
  );
  const tripMap = useMemo(
    () => new Map<string, Trip>(trips.map((trip: Trip) => [trip.id, trip])),
    [trips],
  );

  const filteredDailyProfits = useMemo(
    () =>
      dailyProfits.filter((item: VehicleDailyProfit) => {
        if (startDate && new Date(item.profitDate) < new Date(startDate)) return false;
        if (endDate && new Date(item.profitDate) > new Date(endDate)) return false;
        return true;
      }),
    [dailyProfits, startDate, endDate],
  );

  const filteredMonthlyProfits = useMemo(
    () =>
      monthlyProfits.filter((item: VehicleMonthlyProfit) => {
        if (!selectedMonth) return true;
        return `${item.year}-${String(item.month).padStart(2, '0')}` === selectedMonth;
      }),
    [monthlyProfits, selectedMonth],
  );

  const filteredTripProfits = useMemo(
    () =>
      tripProfits.filter((item: TripProfit) => {
        if (selectedVehicleId && String(item.vehicleId) !== selectedVehicleId) return false;
        const trip = tripMap.get(item.tripId);
        const proxyDate = trip?.startTime ?? item.profitDate;
        if (startDate && new Date(proxyDate) < new Date(startDate)) return false;
        if (endDate && new Date(proxyDate) > new Date(endDate)) return false;
        return true;
      }),
    [tripProfits, selectedVehicleId, startDate, endDate, tripMap],
  );

  const dailyRows = filteredDailyProfits.map((item: VehicleDailyProfit) => [formatDate(item.profitDate), formatCurrency(item.totalRevenue), formatCurrency(item.totalExpense), formatCurrency(item.totalProfit)]);
  const monthlyRows = filteredMonthlyProfits.map((item: VehicleMonthlyProfit) => [formatMonth(item.year, item.month), formatCurrency(item.totalRevenue), formatCurrency(item.totalExpense), formatCurrency(item.totalProfit)]);
  const tripRows = filteredTripProfits.map((item: TripProfit) => {
    const trip = tripMap.get(item.tripId);
    const vehicle = vehicleMap.get(String(item.vehicleId));
    const tripLabel = trip ? `Trip ${trip.id}` : `Trip ${item.tripId}`;
    const vehicleLabel = vehicle ? `${vehicle.licensePlate}` : `Vehicle ${item.vehicleId}`;
    return [tripLabel, vehicleLabel, formatCurrency(item.tripRevenue), formatCurrency(item.totalExpense), formatCurrency(item.tripProfit)];
  });

  function exportCsv() {
    const csvRows: Array<Array<string | number>> = [];
    const csvEscape = (value: string | number) => `"${String(value).replace(/"/g, '""')}"`;

    if (summary) {
      csvRows.push(['Profit summary'], ['Metric', 'Value']);
      csvRows.push(['Total Revenue', summary.totalRevenue]);
      csvRows.push(['Total Expenses', summary.totalExpense]);
      csvRows.push(['Total Profit', summary.totalProfit]);
      csvRows.push([]);
    }

    csvRows.push(['Vehicle daily profit'], ['Date', 'Revenue', 'Expense', 'Profit']);
    filteredDailyProfits.forEach((item: VehicleDailyProfit) => csvRows.push([item.profitDate, item.totalRevenue, item.totalExpense, item.totalProfit]));
    csvRows.push([]);

    csvRows.push(['Vehicle monthly profit'], ['Month', 'Revenue', 'Expense', 'Profit']);
    filteredMonthlyProfits.forEach((item: VehicleMonthlyProfit) => csvRows.push([`${item.year}-${String(item.month).padStart(2, '0')}`, item.totalRevenue, item.totalExpense, item.totalProfit]));
    csvRows.push([]);

    csvRows.push(['Trip profit'], ['Trip', 'Vehicle', 'Revenue', 'Expense', 'Profit']);
    filteredTripProfits.forEach((item: TripProfit) => {
      const trip = tripMap.get(item.tripId);
      const vehicle = vehicleMap.get(String(item.vehicleId));
      const tripLabel = trip ? `Trip ${trip.id}` : `Trip ${item.tripId}`;
      const vehicleLabel = vehicle ? vehicle.licensePlate : `Vehicle ${item.vehicleId}`;
      csvRows.push([tripLabel, vehicleLabel, item.tripRevenue, item.totalExpense, item.tripProfit]);
    });

    const csvText = csvRows.map((row) => row.map(csvEscape).join(',')).join('\n');
    const blob = new Blob([csvText], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `vahanone-profit-report-${new Date().toISOString().slice(0, 10)}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="space-y-6">
      <div className="rounded-3xl bg-white p-6 shadow-sm shadow-slate-200/80">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.16em] text-slate-500">Profit analytics</p>
            <h1 className="mt-2 text-3xl font-semibold text-slate-900">Fleet profitability</h1>
            <p className="mt-2 max-w-2xl text-sm text-slate-600">See revenue, expense, and profit performance for vehicles and trips.</p>
          </div>
          <button
            type="button"
            className="inline-flex items-center rounded-3xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
            onClick={loadProfitData}
          >
            Refresh
          </button>
        </div>
      </div>

      {error && (
        <Card className="rounded-3xl bg-red-50 text-red-700">
          <div className="flex flex-col gap-2">
            <p className="font-semibold">Unable to load profit data</p>
            <p className="text-sm">{error}</p>
          </div>
        </Card>
      )}

      <ProfitFilters
        vehicles={vehicles}
        selectedVehicleId={selectedVehicleId}
        startDate={startDate}
        endDate={endDate}
        selectedMonth={selectedMonth}
        loading={loading}
        onSelectVehicle={setSelectedVehicleId}
        onChangeStartDate={setStartDate}
        onChangeEndDate={setEndDate}
        onChangeMonth={setSelectedMonth}
        onRefresh={loadProfitData}
        onExport={exportCsv}
      />

      <ProfitSummaryCards summary={summary} loading={loading} />

      <div className="grid gap-6 xl:grid-cols-2">
        <ProfitTable
          title="Vehicle daily profit"
          columns={['Date', 'Revenue', 'Expense', 'Profit']}
          rows={dailyRows}
          loading={loading}
          emptyLabel="No daily profit records available for this vehicle."
        />
        <ProfitTable
          title="Vehicle monthly profit"
          columns={['Month', 'Revenue', 'Expense', 'Profit']}
          rows={monthlyRows}
          loading={loading}
          emptyLabel="No monthly profit records available for this vehicle."
        />
      </div>

      <ProfitTable
        title="Trip profit"
        columns={['Trip', 'Vehicle', 'Revenue', 'Expense', 'Profit']}
        rows={tripRows}
        loading={loading}
        emptyLabel="No trip profit records match the current filters."
      />
    </div>
  );
}
