import { Button } from '../../components/ui/Button';
import type { Customer, Invoice, Trip } from '../../types';

interface InvoiceDetailsProps {
  invoice: Invoice;
  customer?: Customer;
  trip?: Trip;
  onClose: () => void;
  onDownload: () => void;
  onMarkPaid: () => Promise<void>;
}

function statusClass(status: Invoice['status']) {
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

export function InvoiceDetails({ invoice, customer, trip, onClose, onDownload, onMarkPaid }: InvoiceDetailsProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-slate-950/40 px-4 py-6">
      <div className="w-full max-w-3xl rounded-3xl bg-white p-6 shadow-2xl shadow-slate-900/10">
        <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-xl font-semibold text-slate-900">Invoice details</h2>
            <p className="text-sm text-slate-500">Review the invoice record and payment status.</p>
          </div>
          <Button type="button" variant="ghost" onClick={onClose}>
            Close
          </Button>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
            <p className="text-sm text-slate-500">Invoice Number</p>
            <p className="mt-2 font-semibold text-slate-900">{invoice.invoiceNumber}</p>
          </div>
          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
            <p className="text-sm text-slate-500">Customer</p>
            <p className="mt-2 font-semibold text-slate-900">{customer?.name ?? 'Unknown'}</p>
          </div>
          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
            <p className="text-sm text-slate-500">Trip</p>
            <p className="mt-2 font-semibold text-slate-900">
              {trip ? `Trip ${trip.id}` : invoice.tripId}
            </p>
          </div>
          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
            <p className="text-sm text-slate-500">Invoice Date</p>
            <p className="mt-2 font-semibold text-slate-900">{formatDate(invoice.invoiceDate)}</p>
          </div>
          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
            <p className="text-sm text-slate-500">Due Date</p>
            <p className="mt-2 font-semibold text-slate-900">{formatDate(invoice.dueDate)}</p>
          </div>
          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
            <p className="text-sm text-slate-500">Amount</p>
            <p className="mt-2 font-semibold text-slate-900">₹{invoice.total.toLocaleString()}</p>
          </div>
          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4 sm:col-span-2">
            <p className="text-sm text-slate-500">Status</p>
            <span className={`mt-2 inline-flex rounded-full px-3 py-1 text-xs font-semibold ${statusClass(invoice.status)}`}>
              {invoice.status}
            </span>
          </div>
        </div>

        <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:justify-end">
          <Button type="button" variant="secondary" onClick={onDownload}>
            Download PDF
          </Button>
          {invoice.status !== 'Paid' && (
            <Button type="button" onClick={async () => await onMarkPaid()}>
              Mark paid
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
