import { useEffect, useState } from 'react';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { getApiErrorMessage } from '../../lib/api';
import type { Vehicle } from '../../types';

interface VehicleFormProps {
  open: boolean;
  vehicle?: Vehicle;
  onClose: () => void;
  onSave: (payload: Omit<Vehicle, 'id'>) => Promise<void>;
}

export function VehicleForm({ open, vehicle, onClose, onSave }: VehicleFormProps) {
  const [vehicleNumber, setVehicleNumber] = useState('');
  const [vehicleType, setVehicleType] = useState('');
  const [make, setMake] = useState('');
  const [model, setModel] = useState('');
  const [seatingCapacity, setSeatingCapacity] = useState(0);
  const [fuelType, setFuelType] = useState('Diesel');
  const [insuranceExpiry, setInsuranceExpiry] = useState('');
  const [permitExpiry, setPermitExpiry] = useState('');
  const [fcExpiry, setFcExpiry] = useState('');
  const [pollutionExpiry, setPollutionExpiry] = useState('');
  const [roadTaxExpiry, setRoadTaxExpiry] = useState('');
  const [emiAmount, setEmiAmount] = useState(0);
  const [emiDueDay, setEmiDueDay] = useState(1);
  const [status, setStatus] = useState<'active' | 'inactive'>('active');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (vehicle) {
      setVehicleNumber(vehicle.licensePlate);
      setVehicleType(vehicle.vehicleType || '');
      setMake(vehicle.make);
      setModel(vehicle.model);
      setSeatingCapacity(vehicle.seatingCapacity ?? 0);
      setFuelType(vehicle.fuelType || 'Diesel');
      setInsuranceExpiry(vehicle.insuranceExpiry || '');
      setPermitExpiry(vehicle.permitExpiry || '');
      setFcExpiry(vehicle.fcExpiry || '');
      setPollutionExpiry(vehicle.pollutionExpiry || '');
      setRoadTaxExpiry(vehicle.roadTaxExpiry || '');
      setEmiAmount(vehicle.emiAmount ?? 0);
      setEmiDueDay(vehicle.emiDueDay ?? 1);
      setStatus(vehicle.status === 'inactive' ? 'inactive' : 'active');
      setError('');
    } else {
      setVehicleNumber('');
      setVehicleType('');
      setMake('');
      setModel('');
      setSeatingCapacity(0);
      setFuelType('Diesel');
      setInsuranceExpiry('');
      setPermitExpiry('');
      setFcExpiry('');
      setPollutionExpiry('');
      setRoadTaxExpiry('');
      setEmiAmount(0);
      setEmiDueDay(1);
      setStatus('active');
      setError('');
    }
  }, [vehicle, open]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError('');
    setSubmitting(true);

    const trimmedVehicleNumber = vehicleNumber.trim();
    if (!trimmedVehicleNumber) {
      setError('Vehicle number is required.');
      setSubmitting(false);
      return;
    }

    try {
      await onSave({
        licensePlate: trimmedVehicleNumber,
        vehicleType: vehicleType.trim(),
        make: make.trim(),
        model: model.trim(),
        seatingCapacity,
        fuelType: fuelType.trim(),
        insuranceExpiry,
        permitExpiry,
        fcExpiry,
        pollutionExpiry,
        roadTaxExpiry,
        emiAmount,
        emiDueDay,
        status,
      });
      onClose();
    } catch (err) {
      setError(getApiErrorMessage(err, 'Unable to save vehicle. Please review the form and try again.'));
    } finally {
      setSubmitting(false);
    }
  }

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-slate-950/40 px-4 py-6">
      <div className="w-full max-w-3xl max-h-[90vh] overflow-y-auto rounded-3xl bg-white p-6 shadow-2xl shadow-slate-900/10">
        <div className="mb-4 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-xl font-semibold text-slate-900">
              {vehicle ? 'Edit Vehicle' : 'Add Vehicle'}
            </h2>
            <p className="text-sm text-slate-500">
              Provide the fleet details and compliance dates for this vehicle.
            </p>
            <p className="mt-1 text-sm text-slate-500">Vehicle number is required; all other fields are optional.</p>
          </div>
          <Button type="button" variant="ghost" onClick={onClose}>
            Close
          </Button>
        </div>

        <form onSubmit={handleSubmit} className="grid gap-4 md:grid-cols-2">
          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Vehicle Number</span>
            <Input value={vehicleNumber} onChange={(event) => setVehicleNumber(event.target.value)} required />
          </label>
          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Vehicle Type</span>
            <Input value={vehicleType} onChange={(event) => setVehicleType(event.target.value)} placeholder="Truck, Bus, Van" />
          </label>
          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Make</span>
            <Input value={make} onChange={(event) => setMake(event.target.value)} />
          </label>
          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Model</span>
            <Input value={model} onChange={(event) => setModel(event.target.value)} />
          </label>
          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Seating Capacity</span>
            <Input value={seatingCapacity} onChange={(event) => setSeatingCapacity(Number(event.target.value))} type="number" min={1} />
          </label>
          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Fuel Type</span>
            <select className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-950 shadow-sm focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200" value={fuelType} onChange={(event) => setFuelType(event.target.value)}>
              <option>Diesel</option>
              <option>Petrol</option>
              <option>CNG</option>
              <option>Electric</option>
            </select>
          </label>
          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Insurance Expiry</span>
            <Input value={insuranceExpiry} onChange={(event) => setInsuranceExpiry(event.target.value)} type="date" />
          </label>
          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Permit Expiry</span>
            <Input value={permitExpiry} onChange={(event) => setPermitExpiry(event.target.value)} type="date" />
          </label>
          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">FC Expiry</span>
            <Input value={fcExpiry} onChange={(event) => setFcExpiry(event.target.value)} type="date" />
          </label>
          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Pollution Expiry</span>
            <Input value={pollutionExpiry} onChange={(event) => setPollutionExpiry(event.target.value)} type="date" />
          </label>
          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Road Tax Expiry</span>
            <Input value={roadTaxExpiry} onChange={(event) => setRoadTaxExpiry(event.target.value)} type="date" />
          </label>
          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">EMI Amount</span>
            <Input value={emiAmount} onChange={(event) => setEmiAmount(Number(event.target.value))} type="number" min={0} />
          </label>
          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">EMI Due Day</span>
            <Input value={emiDueDay} onChange={(event) => setEmiDueDay(Number(event.target.value))} type="number" min={1} max={31} />
          </label>
          <label className="space-y-2 md:col-span-2">
            <span className="text-sm font-medium text-slate-700">Status</span>
            <select className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-950 shadow-sm focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200" value={status} onChange={(event) => setStatus(event.target.value as 'active' | 'inactive')}>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
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
            <Button type="submit" disabled={submitting}>
              {submitting ? 'Saving...' : vehicle ? 'Update vehicle' : 'Add vehicle'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
