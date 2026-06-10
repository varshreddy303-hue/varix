import { useEffect, useMemo, useState } from 'react';
import { Plus, Search, Edit3, Eye, Download, CheckCircle2 } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { InvoiceForm } from '../components/invoices/InvoiceForm';
import { InvoiceDetails } from '../components/invoices/InvoiceDetails';
import { fetchInvoices, createInvoice, updateInvoice, markInvoicePaid } from '../services/invoiceService';
import { fetchCustomers } from '../services/customerService';
import { fetchTrips } from '../services/tripService';
import type { Customer, Invoice, InvoiceStatus, Trip } from '../types';

const statusOptions: InvoiceStatus[] = ['Draft', 'Sent', 'Paid', 'Overdue'];

type StatusFilter = InvoiceStatus | 'All';

function statusClass(status: InvoiceStatus) {
  switch (status) {
    case 'Draft':
      return 'bg-slate-100 text-slate-700';
    case 'Sent':
      return 'bg-sky-100 text-sky-700';
    case 'Paid':
      return 'bg-emerald-100 text-emerald-700';
    case 'Overdue':
      return 'bg-red-100 text-red-700';
    default:
      return 'bg-slate-100 text-slate-700';
  }
}

function formatDate(value: string) {
  return new Date(value).toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

export function Invoices() {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [trips, setTrips] = useState<Trip[]>([]);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('All');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [formOpen, setFormOpen] = useState(false);
  const [activeInvoice, setActiveInvoice] = useState<Invoice | undefined>(undefined);
  const [detailsInvoice, setDetailsInvoice] = useState<Invoice | undefined>(undefined);

  useEffect(() => {
    refresh();
  }, []);

  const customerMap = useMemo(() => new Map(customers.map((customer) => [customer.id, customer])), [customers]);
  const tripMap = useMemo(() => new Map(trips.map((trip) => [trip.id, trip])), [trips]);

  const invoicesWithLabels = useMemo(
    () =>
      invoices.map((invoice) => ({
        ...invoice,
        customerName: customerMap.get(invoice.customerId)?.name ?? 'Unknown',
        tripLabel: tripMap.get(invoice.tripId)
          ? `Trip ${tripMap.get(invoice.tripId)?.id}`
          : invoice.tripId,
      })),
    [invoices, customerMap, tripMap],
  );

  const filteredInvoices = useMemo(() => {
    const normalized = search.toLowerCase().trim();
    return invoicesWithLabels.filter((invoice) => {
      const matchesSearch = [
        invoice.invoiceNumber,
        invoice.customerName,
        invoice.tripLabel,
        invoice.status,
      ]
        .join(' ')
        .toLowerCase()
        .includes(normalized);

      const matchesStatus = statusFilter === 'All' || invoice.status === statusFilter;
      return matchesSearch && matchesStatus;
    });
  }, [invoicesWithLabels, search, statusFilter]);

  async function refresh() {
    setLoading(true);
    setError('');
    try {
      const [invoiceData, customerData, tripData] = await Promise.all([
        fetchInvoices(),
        fetchCustomers(),
        fetchTrips(),
      ]);
      setInvoices(invoiceData);
      setCustomers(customerData);
      setTrips(tripData);
    } catch {
      setError('Unable to load invoices. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  async function handleSaveInvoice(payload: Omit<Invoice, 'id' | 'status' | 'total'>) {
    setLoading(true);
    setError('');
    try {
      if (activeInvoice) {
        await updateInvoice(activeInvoice.id, payload);
      } else {
        await createInvoice(payload);
      }
      setFormOpen(false);
      setActiveInvoice(undefined);
      await refresh();
    } catch {
      setError('Unable to save invoice. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  async function handleMarkPaid(invoiceId: string) {
    setLoading(true);
    setError('');
    try {
      await markInvoicePaid(invoiceId);
      await refresh();
      if (detailsInvoice?.id === invoiceId) {
        setDetailsInvoice((current) => (current ? { ...current, status: 'Paid' } : current));
      }
    } catch {
      setError('Unable to mark invoice as paid.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="rounded-3xl bg-white p-6 shadow-sm shadow-slate-200/80 sm:flex sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Invoices</h1>
          <p className="mt-1 text-sm text-slate-600">Manage billing, payment status, and invoice delivery for customers.</p>
        </div>
        <div className="mt-4 flex flex-col gap-3 sm:mt-0 sm:flex-row sm:items-center">
          <Button
            onClick={() => {
              setActiveInvoice(undefined);
              setFormOpen(true);
            }}
          >
            <Plus className="mr-2 h-4 w-4" />
            Create invoice
          </Button>
          <Button variant="secondary" onClick={refresh} disabled={loading}>
            Refresh
          </Button>
        </div>
      </div>

      <Card>
        <div className="mb-6 grid gap-4 lg:grid-cols-[1fr_auto] xl:grid-cols-[1fr_auto_auto] xl:items-end">
          <div className="relative max-w-md">
            <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <Input
              className="pl-11"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search invoices"
            />
          </div>
          <div className="flex items-center gap-3">
            <label className="sr-only" htmlFor="status-filter">
              Filter by status
            </label>
            <select
              id="status-filter"
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
          <p className="text-sm text-slate-500 xl:text-right">
            {loading ? 'Loading invoices…' : `${filteredInvoices.length} invoice${filteredInvoices.length === 1 ? '' : 's'}`}
          </p>
        </div>

        {error && (
          <div className="mb-6 rounded-3xl bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
        )}

        {loading ? (
          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-10 text-center text-slate-500">Loading invoices...</div>
        ) : filteredInvoices.length === 0 ? (
          <div className="rounded-3xl border border-dashed border-slate-200 bg-slate-50 p-10 text-center text-slate-500">
            <p className="mb-3 text-lg font-semibold text-slate-900">No invoices found</p>
            <p>Create your first invoice with the Create invoice button.</p>
          </div>
        ) : (
          <div className="overflow-hidden rounded-3xl border border-slate-200">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
                <thead className="bg-slate-50 text-slate-600">
                  <tr>
                    <th className="px-6 py-4 font-medium">Invoice Number</th>
                    <th className="px-6 py-4 font-medium">Customer</th>
                    <th className="px-6 py-4 font-medium">Trip</th>
                    <th className="px-6 py-4 font-medium">Invoice Date</th>
                    <th className="px-6 py-4 font-medium">Due Date</th>
                    <th className="px-6 py-4 font-medium">Amount</th>
                    <th className="px-6 py-4 font-medium">Status</th>
                    <th className="px-6 py-4 font-medium text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 bg-white">
                  {filteredInvoices.map((invoice) => (
                    <tr key={invoice.id} className="hover:bg-slate-50">
                      <td className="px-6 py-4 font-medium text-slate-900">{invoice.invoiceNumber}</td>
                      <td className="px-6 py-4 text-slate-600">{invoice.customerName}</td>
                      <td className="px-6 py-4 text-slate-600">{invoice.tripLabel}</td>
                      <td className="px-6 py-4 text-slate-600">{formatDate(invoice.invoiceDate)}</td>
                      <td className="px-6 py-4 text-slate-600">{formatDate(invoice.dueDate)}</td>
                      <td className="px-6 py-4 text-slate-600">₹{invoice.total.toLocaleString()}</td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${statusClass(invoice.status)}`}>
                          {invoice.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="inline-flex flex-wrap items-center justify-end gap-2">
                          <Button
                            type="button"
                            variant="secondary"
                            className="inline-flex items-center gap-2"
                            onClick={() => setDetailsInvoice(invoice)}
                          >
                            <Eye className="h-4 w-4" />
                            View
                          </Button>
                          <Button
                            type="button"
                            variant="secondary"
                            className="inline-flex items-center gap-2"
                            onClick={() => {
                              setActiveInvoice(invoice);
                              setFormOpen(true);
                            }}
                          >
                            <Edit3 className="h-4 w-4" />
                            Edit
                          </Button>
                          {invoice.status !== 'Paid' && (
                            <Button
                              type="button"
                              variant="ghost"
                              className="inline-flex items-center gap-2 text-emerald-600 hover:bg-emerald-50"
                              onClick={() => handleMarkPaid(invoice.id)}
                            >
                              <CheckCircle2 className="h-4 w-4" />
                              Mark paid
                            </Button>
                          )}
                          <Button
                            type="button"
                            variant="ghost"
                            className="inline-flex items-center gap-2 text-slate-700 hover:bg-slate-50"
                            onClick={() => window.alert('Download PDF placeholder')}
                          >
                            <Download className="h-4 w-4" />
                            PDF
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

      <InvoiceForm
        open={formOpen}
        invoice={activeInvoice}
        customers={customers}
        trips={trips}
        onClose={() => setFormOpen(false)}
        onSave={handleSaveInvoice}
      />

      {detailsInvoice && (
        <InvoiceDetails
          invoice={detailsInvoice}
          customer={customerMap.get(detailsInvoice.customerId)}
          trip={tripMap.get(detailsInvoice.tripId)}
          onClose={() => setDetailsInvoice(undefined)}
          onDownload={() => window.alert('Download PDF placeholder')}
          onMarkPaid={async () => {
            await handleMarkPaid(detailsInvoice.id);
            setDetailsInvoice(undefined);
          }}
        />
      )}
    </div>
  );
}
