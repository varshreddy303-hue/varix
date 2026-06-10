import { Download, RefreshCcw } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { Input } from '../../components/ui/Input';
import type { Vehicle } from '../../types';

interface ProfitFiltersProps {
  vehicles: Vehicle[];
  selectedVehicleId: string;
  startDate: string;
  endDate: string;
  selectedMonth: string;
  loading: boolean;
  onSelectVehicle: (vehicleId: string) => void;
  onChangeStartDate: (value: string) => void;
  onChangeEndDate: (value: string) => void;
  onChangeMonth: (value: string) => void;
  onRefresh: () => void;
  onExport: () => void;
}

export function ProfitFilters({
  vehicles,
  selectedVehicleId,
  startDate,
  endDate,
  selectedMonth,
  loading,
  onSelectVehicle,
  onChangeStartDate,
  onChangeEndDate,
  onChangeMonth,
  onRefresh,
  onExport,
}: ProfitFiltersProps) {
  return (
    <Card className="rounded-3xl p-6">
      <div className="mb-4 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.16em] text-slate-500">Profit filters</p>
          <h2 className="mt-2 text-xl font-semibold text-slate-900">Choose vehicle and date range</h2>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <Button type="button" variant="secondary" onClick={onRefresh} disabled={loading}>
            <RefreshCcw className="mr-2 h-4 w-4" />
            Refresh
          </Button>
          <Button type="button" onClick={onExport} disabled={loading}>
            <Download className="mr-2 h-4 w-4" />
            Export CSV
          </Button>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-4">
        <label className="space-y-2">
          <span className="text-sm font-medium text-slate-700">Vehicle</span>
          <select
            value={selectedVehicleId}
            onChange={(event) => onSelectVehicle(event.target.value)}
            className="w-full rounded-3xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 shadow-sm focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200"
          >
            {vehicles.map((vehicle) => (
              <option key={vehicle.id} value={vehicle.id}>
                {vehicle.licensePlate} • {vehicle.make} {vehicle.model}
              </option>
            ))}
          </select>
        </label>

        <label className="space-y-2">
          <span className="text-sm font-medium text-slate-700">Start date</span>
          <Input
            type="date"
            value={startDate}
            onChange={(event) => onChangeStartDate(event.target.value)}
          />
        </label>

        <label className="space-y-2">
          <span className="text-sm font-medium text-slate-700">End date</span>
          <Input
            type="date"
            value={endDate}
            onChange={(event) => onChangeEndDate(event.target.value)}
          />
        </label>

        <label className="space-y-2">
          <span className="text-sm font-medium text-slate-700">Month</span>
          <Input
            type="month"
            value={selectedMonth}
            onChange={(event) => onChangeMonth(event.target.value)}
          />
        </label>
      </div>
    </Card>
  );
}
