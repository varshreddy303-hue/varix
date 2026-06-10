import { useEffect, useMemo, useState } from 'react';
import { Search, Filter } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { RenewalSummaryCards } from '../components/renewals/RenewalSummaryCards';
import { RenewalTable, type RenewalDocumentType, type RenewalRow, type RenewalStatus } from '../components/renewals/RenewalTable';
import { fetchVehicles } from '../services/vehicleService';
import type { Vehicle } from '../types';

const documentTypes: RenewalDocumentType[] = ['Insurance', 'Permit', 'FC', 'Pollution', 'Road Tax'];
const statusOptions: RenewalStatus[] = ['Expired', 'Expiring Soon', 'Valid'];

type DocumentTypeFilter = RenewalDocumentType | 'All';
type StatusFilter = RenewalStatus | 'All';

type ExpiryField = {
  type: RenewalDocumentType;
  label: string;
  field: keyof Pick<Vehicle, 'insuranceExpiry' | 'permitExpiry' | 'fcExpiry' | 'pollutionExpiry' | 'roadTaxExpiry'>;
};

const expiryFields: ExpiryField[] = [
  { type: 'Insurance', label: 'Insurance', field: 'insuranceExpiry' },
  { type: 'Permit', label: 'Permit', field: 'permitExpiry' },
  { type: 'FC', label: 'FC', field: 'fcExpiry' },
  { type: 'Pollution', label: 'Pollution', field: 'pollutionExpiry' },
  { type: 'Road Tax', label: 'Road Tax', field: 'roadTaxExpiry' },
];

function getExpiryStatus(daysRemaining: number) {
  if (daysRemaining < 0) return 'Expired' as RenewalStatus;
  if (daysRemaining <= 30) return 'Expiring Soon' as RenewalStatus;
  return 'Valid' as RenewalStatus;
}

function getDaysRemaining(expiryDate: string) {
  const now = new Date();
  const expiry = new Date(expiryDate);
  const msPerDay = 1000 * 60 * 60 * 24;
  return Math.ceil((expiry.getTime() - now.getTime()) / msPerDay);
}

function getNextEmiDate(emiDueDay: number) {
  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth();
  const candidate = new Date(year, month, Math.min(emiDueDay, 28));

  if (candidate.getTime() >= now.getTime()) {
    return candidate;
  }

  return new Date(year, month + 1, Math.min(emiDueDay, 28));
}

function formatDate(value: string) {
  return new Date(value).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
}

export function Renewals() {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [docTypeFilter, setDocTypeFilter] = useState<DocumentTypeFilter>('All');
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('All');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError('');
      try {
        const vehicleData = await fetchVehicles();
        setVehicles(vehicleData);
      } catch {
        setError('Unable to load vehicles. Please try again.');
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

  const renewalItems = useMemo(() => {
    return vehicles.flatMap((vehicle) =>
      expiryFields.map((expiry) => {
        const expiryDate = vehicle[expiry.field] as string;
        const daysRemaining = getDaysRemaining(expiryDate);
        const status = getExpiryStatus(daysRemaining);
        return {
          id: `${vehicle.id}-${expiry.type}`,
          vehicleNumber: vehicle.licensePlate,
          documentType: expiry.type,
          expiryDate: formatDate(expiryDate),
          rawExpiry: expiryDate,
          daysRemaining,
          status,
        };
      }),
    );
  }, [vehicles]);

  const upcomingEmiCount = useMemo(() => {
    const now = new Date();
    const threshold = 30;
    return vehicles.filter((vehicle) => {
      if (vehicle.emiAmount <= 0) return false;
      const emiDate = getNextEmiDate(vehicle.emiDueDay);
      return Math.ceil((emiDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)) <= threshold;
    }).length;
  }, [vehicles]);

  const expiredCount = useMemo(() => renewalItems.filter((item) => item.status === 'Expired').length, [renewalItems]);
  const expiringSoonCount = useMemo(() => renewalItems.filter((item) => item.status === 'Expiring Soon').length, [renewalItems]);

  const filteredItems = useMemo(() => {
    const normalizedSearch = search.toLowerCase().trim();
    return renewalItems
      .filter((item) => {
        const matchesSearch = [item.vehicleNumber, item.documentType, item.status].join(' ').toLowerCase().includes(normalizedSearch);
        const matchesDocType = docTypeFilter === 'All' || item.documentType === docTypeFilter;
        const matchesStatus = statusFilter === 'All' || item.status === statusFilter;
        return matchesSearch && matchesDocType && matchesStatus;
      })
      .sort((a, b) => {
        const left = new Date(a.rawExpiry).getTime();
        const right = new Date(b.rawExpiry).getTime();
        return sortDirection === 'asc' ? left - right : right - left;
      });
  }, [renewalItems, search, docTypeFilter, statusFilter, sortDirection]);

  return (
    <div className="space-y-6">
      <div className="rounded-3xl bg-white p-6 shadow-sm shadow-slate-200/80 sm:flex sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Renewals</h1>
          <p className="mt-1 text-sm text-slate-600">Track permit, insurance, and tax renewals for your vehicle fleet.</p>
        </div>
      </div>

      <RenewalSummaryCards
        loading={loading}
        expiredCount={expiredCount}
        expiringSoonCount={expiringSoonCount}
        upcomingEmiCount={upcomingEmiCount}
      />

      <Card>
        <div className="mb-6 grid gap-4 lg:grid-cols-[1fr_auto_auto] xl:grid-cols-[1fr_auto_auto_auto] xl:items-end">
          <div className="relative max-w-md">
            <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <Input
              className="pl-11"
              placeholder="Search vehicles"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
            />
          </div>

          <div className="flex items-center gap-3">
            <Filter className="h-4 w-4 text-slate-400" />
            <select
              className="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 shadow-sm focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200"
              value={docTypeFilter}
              onChange={(event) => setDocTypeFilter(event.target.value as DocumentTypeFilter)}
            >
              <option value="All">All document types</option>
              {documentTypes.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-3">
            <Filter className="h-4 w-4 text-slate-400" />
            <select
              className="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 shadow-sm focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200"
              value={statusFilter}
              onChange={(event) => setStatusFilter(event.target.value as StatusFilter)}
            >
              <option value="All">All statuses</option>
              {statusOptions.map((status) => (
                <option key={status} value={status}>
                  {status}
                </option>
              ))}
            </select>
          </div>
        </div>

        {error && <div className="mb-6 rounded-3xl bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

        {loading ? (
          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-10 text-center text-slate-500">Loading renewal data...</div>
        ) : filteredItems.length === 0 ? (
          <div className="rounded-3xl border border-dashed border-slate-200 bg-slate-50 p-10 text-center text-slate-500">
            <p className="mb-3 text-lg font-semibold text-slate-900">No renewal records found</p>
            <p>Adjust the search or filters to find matching vehicle documents.</p>
          </div>
        ) : (
          <RenewalTable
            items={filteredItems}
            sortDirection={sortDirection}
            onSortChange={() => setSortDirection((current) => (current === 'asc' ? 'desc' : 'asc'))}
          />
        )}
      </Card>
    </div>
  );
}
