import { useEffect, useMemo, useState } from 'react';
import { Plus, Search } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { fetchMaintenanceSchedules, createMaintenanceSchedule } from '../services/maintenanceService';
import { fetchVehicles } from '../services/vehicleService';
import type { MaintenanceSchedule, Vehicle } from '../types';

function formatDateTime(value: string) {
  return new Date(value).toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function Maintenance() {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [schedules, setSchedules] = useState<MaintenanceSchedule[]>([]);
  const [selectedVehicle, setSelectedVehicle] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [reason, setReason] = useState('');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError('');
      try {
        const [vehiclesData, schedulesData] = await Promise.all([
          fetchVehicles(),
          fetchMaintenanceSchedules(),
        ]);
        setVehicles(vehiclesData);
        setSchedules(schedulesData);
      } catch {
        setError('Unable to load maintenance scheduling data.');
      } finally {
        setLoading(false);
      }
    }

    void load();
  }, []);

  const filteredSchedules = useMemo(() => {
    const normalized = search.toLowerCase().trim();
    return schedules.filter((schedule) => {
      const vehicle = vehicles.find((vehicleItem) => vehicleItem.id === schedule.vehicleId)?.licensePlate ?? '';
      return [vehicle, schedule.reason, schedule.status]
        .join(' ')
        .toLowerCase()
        .includes(normalized);
    });
  }, [schedules, vehicles, search]);

  async function refresh() {
    setLoading(true);
    setError('');
    try {
      const [vehiclesData, schedulesData] = await Promise.all([
        fetchVehicles(),
        fetchMaintenanceSchedules(),
      ]);
      setVehicles(vehiclesData);
      setSchedules(schedulesData);
    } catch {
      setError('Unable to refresh maintenance schedule data.');
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit() {
    if (!selectedVehicle || !startDate || !endDate || !reason) {
      setError('Please select a vehicle, date range, and reason for maintenance.');
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      await createMaintenanceSchedule({
        vehicleId: selectedVehicle,
        startDate: new Date(startDate).toISOString(),
        endDate: new Date(endDate).toISOString(),
        reason,
        status: 'scheduled',
      });
      setSelectedVehicle('');
      setStartDate('');
      setEndDate('');
      setReason('');
      await refresh();
    } catch {
      setError('Unable to schedule maintenance. Please verify the dates and try again.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="rounded-3xl bg-white p-6 shadow-sm shadow-slate-200/80 sm:flex sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Maintenance schedule</h1>
          <p className="mt-1 text-sm text-slate-600">Plan service windows that prevent vehicle dispatch during downtime.</p>
        </div>
        <Button onClick={refresh}>Refresh</Button>
      </div>

      <Card className="rounded-3xl border border-slate-200 p-6">
        <div className="grid gap-4 xl:grid-cols-[1.2fr_1fr]">
          <div>
            <label className="block text-sm font-medium text-slate-700">Vehicle</label>
            <select
              value={selectedVehicle}
              onChange={(event) => setSelectedVehicle(event.target.value)}
              className="mt-2 w-full rounded-3xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700 shadow-sm focus:border-slate-400 focus:outline-none"
            >
              <option value="">Select a vehicle</option>
              {vehicles.map((vehicle) => (
                <option key={vehicle.id} value={vehicle.id}>{vehicle.licensePlate}</option>
              ))}
            </select>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-slate-700">Start date</label>
              <Input type="datetime-local" value={startDate} onChange={(event) => setStartDate(event.target.value)} />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700">End date</label>
              <Input type="datetime-local" value={endDate} onChange={(event) => setEndDate(event.target.value)} />
            </div>
          </div>

          <div className="sm:col-span-2">
            <label className="block text-sm font-medium text-slate-700">Reason</label>
            <textarea
              rows={3}
              className="mt-2 w-full rounded-3xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700 shadow-sm focus:border-slate-400 focus:outline-none"
              value={reason}
              onChange={(event) => setReason(event.target.value)}
            />
          </div>

          <div className="sm:col-span-2 flex flex-wrap items-center gap-3">
            <Button onClick={handleSubmit} disabled={submitting}>
              <Plus className="mr-2 h-4 w-4" />
              Schedule maintenance
            </Button>
            <span className="text-sm text-slate-500">Maintenance windows will block conflicting bookings.</span>
          </div>
        </div>

        {error && <div className="mt-4 rounded-3xl bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}
      </Card>

      <Card className="rounded-3xl border border-slate-200 p-6">
        <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-xl font-semibold text-slate-900">Scheduled maintenance</h2>
            <p className="text-sm text-slate-500">Review future downtime windows for fleet vehicles.</p>
          </div>
          <div className="relative w-full max-w-md">
            <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <Input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search schedules" className="pl-11" />
          </div>
        </div>

        {loading ? (
          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-10 text-center text-slate-500">Loading schedules...</div>
        ) : filteredSchedules.length === 0 ? (
          <div className="rounded-3xl border border-dashed border-slate-200 bg-slate-50 p-10 text-center text-slate-500">
            No maintenance windows scheduled yet.
          </div>
        ) : (
          <div className="space-y-4">
            {filteredSchedules.map((schedule) => (
              <div key={schedule.id} className="rounded-3xl border border-slate-200 bg-white p-4 shadow-sm shadow-slate-100">
                <div className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
                  <div>
                    <p className="text-sm text-slate-500">{vehicles.find((vehicle) => vehicle.id === schedule.vehicleId)?.licensePlate ?? 'Unknown vehicle'}</p>
                    <p className="mt-2 text-lg font-semibold text-slate-900">{schedule.reason}</p>
                    <p className="mt-2 text-slate-600">{formatDateTime(schedule.startDate)} → {formatDateTime(schedule.endDate)}</p>
                  </div>
                  <div className="text-right">
                    <span className="inline-flex rounded-full bg-amber-100 px-3 py-1 text-xs font-semibold text-amber-700">{schedule.status}</span>
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
