import { useEffect, useMemo, useState } from 'react';
import { Plus, Search, Filter, Edit3, Trash2 } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { Input } from '../components/ui/Input';
import { VehicleForm } from '../components/vehicles/VehicleForm';
import { fetchVehicles, createVehicle, updateVehicle, deleteVehicle } from '../services/vehicleService';
import type { Vehicle } from '../types';

const statuses = [
  { label: 'All Vehicles', value: 'all' },
  { label: 'Active', value: 'active' },
  { label: 'Inactive', value: 'inactive' },
];

function getExpiryState(dateString: string) {
  if (!dateString) return 'missing';
  const expiry = new Date(dateString);
  const now = new Date();
  const diffDays = Math.ceil((expiry.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));

  if (diffDays < 0) return 'expired';
  if (diffDays <= 30) return 'warning';
  return 'valid';
}

function expiryBadge(label: string, state: string) {
  const className =
    state === 'expired'
      ? 'bg-red-100 text-red-700'
      : state === 'warning'
      ? 'bg-amber-100 text-amber-700'
      : 'bg-emerald-100 text-emerald-700';

  return <span className={`rounded-full px-2 py-1 text-[11px] font-semibold ${className}`}>{label}</span>;
}

export function Vehicles() {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'inactive'>('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [activeVehicle, setActiveVehicle] = useState<Vehicle | undefined>(undefined);

  useEffect(() => {
    async function loadVehicles() {
      setLoading(true);
      setError('');
      try {
        const data = await fetchVehicles();
        setVehicles(data);
      } catch (err) {
        setError('Unable to load vehicles. Please try again later.');
      } finally {
        setLoading(false);
      }
    }

    loadVehicles();
  }, []);

  const filteredVehicles = useMemo(() => {
    const normalized = search.toLowerCase().trim();
    return vehicles
      .filter((vehicle) => statusFilter === 'all' || vehicle.status === statusFilter)
      .filter((vehicle) =>
        [vehicle.licensePlate, vehicle.vehicleType, vehicle.make, vehicle.model, vehicle.fuelType]
          .join(' ')
          .toLowerCase()
          .includes(normalized),
      );
  }, [vehicles, search, statusFilter]);

  async function refreshVehicles() {
    setLoading(true);
    setError('');
    try {
      const data = await fetchVehicles();
      setVehicles(data);
    } catch {
      setError('Unable to refresh vehicles.');
    } finally {
      setLoading(false);
    }
  }

  async function handleSave(payload: Omit<Vehicle, 'id'>) {
    if (activeVehicle) {
      await updateVehicle(activeVehicle.id, payload);
    } else {
      await createVehicle(payload);
    }
    await refreshVehicles();
  }

  async function handleDelete(vehicleId: string) {
    const confirmed = window.confirm('Remove this vehicle? This action is a soft delete if your backend supports it.');
    if (!confirmed) return;

    setLoading(true);
    setError('');
    try {
      await deleteVehicle(vehicleId);
      await refreshVehicles();
    } catch {
      setError('Unable to remove this vehicle.');
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 rounded-3xl bg-white p-6 shadow-sm shadow-slate-200/80 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Vehicles</h1>
          <p className="mt-1 text-sm text-slate-600">Manage your fleet, compliance dates, and financial details.</p>
        </div>
        <Button
          onClick={() => {
            setActiveVehicle(undefined);
            setModalOpen(true);
          }}
        >
          <Plus className="mr-2 h-4 w-4" />
          Add Vehicle
        </Button>
      </div>

      <Card>
        <div className="mb-6 grid gap-4 md:grid-cols-[1fr_auto] md:items-center">
          <div className="relative max-w-sm">
            <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <Input
              className="pl-11"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search vehicles"
            />
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <div className="inline-flex items-center gap-2 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
              <Filter className="h-4 w-4 text-slate-500" />
              <select
                className="appearance-none bg-transparent outline-none"
                value={statusFilter}
                onChange={(event) => setStatusFilter(event.target.value as 'all' | 'active' | 'inactive')}
              >
                {statuses.map((item) => (
                  <option key={item.value} value={item.value}>
                    {item.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="text-sm text-slate-500">
              {loading ? 'Loading vehicles…' : `${filteredVehicles.length} vehicles`}
            </div>
          </div>
        </div>

        {error && (
          <div className="mb-6 rounded-3xl bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        {loading ? (
          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-10 text-center text-slate-500">
            Loading vehicles...
          </div>
        ) : filteredVehicles.length === 0 ? (
          <div className="rounded-3xl border border-dashed border-slate-200 bg-slate-50 p-10 text-center text-slate-500">
            <p className="mb-3 text-lg font-semibold text-slate-900">No vehicles found</p>
            <p>Use the Add Vehicle button to create a new fleet entry or update your search filters.</p>
          </div>
        ) : (
          <div className="overflow-hidden rounded-3xl border border-slate-200">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
                <thead className="bg-slate-50 text-slate-600">
                  <tr>
                    <th className="px-6 py-4 font-medium">Vehicle Number</th>
                    <th className="px-6 py-4 font-medium">Type</th>
                    <th className="px-6 py-4 font-medium">Make / Model</th>
                    <th className="px-6 py-4 font-medium">Seating</th>
                    <th className="px-6 py-4 font-medium">Fuel</th>
                    <th className="px-6 py-4 font-medium">Compliance</th>
                    <th className="px-6 py-4 font-medium">EMI</th>
                    <th className="px-6 py-4 font-medium">Status</th>
                    <th className="px-6 py-4 font-medium text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 bg-white">
                  {filteredVehicles.map((vehicle) => (
                    <tr key={vehicle.id} className="hover:bg-slate-50">
                      <td className="px-6 py-4 font-medium text-slate-900">{vehicle.licensePlate}</td>
                      <td className="px-6 py-4 text-slate-600">{vehicle.vehicleType}</td>
                      <td className="px-6 py-4 text-slate-600">{vehicle.make} {vehicle.model}</td>
                      <td className="px-6 py-4 text-slate-600">{vehicle.seatingCapacity}</td>
                      <td className="px-6 py-4 text-slate-600">{vehicle.fuelType}</td>
                      <td className="px-6 py-4 space-y-2 text-slate-700">
                        {expiryBadge('Insurance', getExpiryState(vehicle.insuranceExpiry))}
                        {expiryBadge('Permit', getExpiryState(vehicle.permitExpiry))}
                        {expiryBadge('FC', getExpiryState(vehicle.fcExpiry))}
                        {expiryBadge('Pollution', getExpiryState(vehicle.pollutionExpiry))}
                        {expiryBadge('Road Tax', getExpiryState(vehicle.roadTaxExpiry))}
                      </td>
                      <td className="px-6 py-4 text-slate-600">₹{vehicle.emiAmount.toLocaleString()}<span className="block text-xs text-slate-400">Due day {vehicle.emiDueDay}</span></td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${vehicle.status === 'active' ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-600'}`}>
                          {vehicle.status === 'active' ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="inline-flex items-center gap-2">
                          <Button
                            type="button"
                            variant="secondary"
                            className="inline-flex items-center gap-2"
                            onClick={() => {
                              setActiveVehicle(vehicle);
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
                            onClick={() => handleDelete(vehicle.id)}
                          >
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

      <VehicleForm
        open={modalOpen}
        vehicle={activeVehicle}
        onClose={() => setModalOpen(false)}
        onSave={handleSave}
      />
    </div>
  );
}
