import { useEffect, useState, type FormEvent } from 'react';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { getApiErrorMessage } from '../../lib/api';
import type { Customer, Invoice, Trip } from '../../types';

type InvoiceFormPayload = Omit<Invoice, 'id' | 'status' | 'total'>;

interface InvoiceFormProps {
  open: boolean;
  invoice?: Invoice;
  customers: Customer[];
  trips: Trip[];
  onClose: () => void;
  onSave: (payload: InvoiceFormPayload) => Promise<void>;
}

export function InvoiceForm({ open, invoice, customers, trips, onClose, onSave }: InvoiceFormProps) {
  const [invoiceNumber, setInvoiceNumber] = useState('');
  const [customerId, setCustomerId] = useState('');
  const [tripId, setTripId] = useState('');
  const [invoiceDate, setInvoiceDate] = useState('');
  const [dueDate, setDueDate] = useState('');
  const [subtotal, setSubtotal] = useState(0);
  const [taxAmount, setTaxAmount] = useState(0);
  const [notes, setNotes] = useState('');
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (invoice) {
      setInvoiceNumber(invoice.invoiceNumber);
      setCustomerId(invoice.customerId);
      setTripId(invoice.tripId);
      setInvoiceDate(invoice.invoiceDate);
      setDueDate(invoice.dueDate);
      setSubtotal(invoice.subtotal);
      setTaxAmount(invoice.taxAmount);
      setNotes(invoice.notes);
      setError('');
    } else {
      setInvoiceNumber('');
      setCustomerId(customers[0]?.id ?? '');
      setTripId(trips[0]?.id ?? '');
      setInvoiceDate('');
      setDueDate('');
      setSubtotal(0);
      setTaxAmount(0);
      setNotes('');
      setError('');
    }
  }, [invoice, open, customers, trips]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError('');

    if (!invoiceNumber || !customerId || !tripId || !invoiceDate || !dueDate) {
      setError('Please complete all required fields.');
      return;
    }

    const computedTotal = subtotal + taxAmount;
    if (computedTotal <= 0) {
      setError('Invoice amount must be greater than zero.');
      return;
    }

    if (subtotal < 0 || taxAmount < 0) {
      setError('Subtotal and tax amount must be zero or greater.');
      return;
    }

    if (new Date(dueDate) < new Date(invoiceDate)) {
      setError('Due date must be the same day or after invoice date.');
      return;
    }

    setSaving(true);
    try {
      await onSave({
        invoiceNumber,
        customerId,
        tripId,
        invoiceDate,
        dueDate,
        subtotal,
        taxAmount,
        notes,
      });
      onClose();
    } catch (err) {
      setError(getApiErrorMessage(err, 'Unable to save invoice. Please try again.'));
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
            <h2 className="text-xl font-semibold text-slate-900">{invoice ? 'Edit invoice' : 'Create invoice'}</h2>
            <p className="text-sm text-slate-500">Enter invoice details and connect it to a customer and trip.</p>
          </div>
          <Button type="button" variant="ghost" onClick={onClose}>
            Close
          </Button>
        </div>

        <form onSubmit={handleSubmit} className="grid gap-4 md:grid-cols-2">
          <label className="space-y-2 md:col-span-2">
            <span className="text-sm font-medium text-slate-700">Invoice Number</span>
            <Input value={invoiceNumber} onChange={(event) => setInvoiceNumber(event.target.value)} required />
          </label>

          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Customer</span>
            <select
              className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 shadow-sm focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200"
              value={customerId}
              onChange={(event) => setCustomerId(event.target.value)}
              required
            >
              <option value="">Select customer</option>
              {customers.map((customer) => (
                <option key={customer.id} value={customer.id}>
                  {customer.name}
                </option>
              ))}
            </select>
          </label>

          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Trip</span>
            <select
              className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 shadow-sm focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200"
              value={tripId}
              onChange={(event) => setTripId(event.target.value)}
              required
            >
              <option value="">Select trip</option>
              {trips.map((trip) => (
                <option key={trip.id} value={trip.id}>
                  Trip {trip.id}
                </option>
              ))}
            </select>
          </label>

          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Invoice Date</span>
            <Input value={invoiceDate} onChange={(event) => setInvoiceDate(event.target.value)} type="date" required />
          </label>

          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Due Date</span>
            <Input value={dueDate} onChange={(event) => setDueDate(event.target.value)} type="date" required />
          </label>

          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Subtotal</span>
            <Input
              type="number"
              min={0}
              step="0.01"
              value={subtotal}
              onChange={(event) => setSubtotal(Number(event.target.value))}
              required
            />
          </label>

          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Tax amount</span>
            <Input
              type="number"
              min={0}
              step="0.01"
              value={taxAmount}
              onChange={(event) => setTaxAmount(Number(event.target.value))}
              required
            />
          </label>

          <div className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Total</span>
            <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900">
              ₹{(subtotal + taxAmount).toLocaleString()}
            </div>
          </div>

          <label className="space-y-2 md:col-span-2">
            <span className="text-sm font-medium text-slate-700">Notes</span>
            <textarea
              className="h-28 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 shadow-sm placeholder:text-slate-400 focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200"
              value={notes}
              onChange={(event) => setNotes(event.target.value)}
            />
          </label>

          {error && (
            <div className="md:col-span-2 rounded-3xl bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
          )}

          <div className="md:col-span-2 flex flex-col gap-3 sm:flex-row sm:justify-end">
            <Button type="button" variant="secondary" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={saving}>
              {saving ? 'Saving...' : invoice ? 'Update invoice' : 'Create invoice'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
