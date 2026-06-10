import { useEffect, useState } from 'react';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { getApiErrorMessage } from '../../lib/api';
import type { Customer } from '../../types';

interface CustomerFormProps {
  open: boolean;
  customer?: Customer;
  onClose: () => void;
  onSave: (payload: Omit<Customer, 'id'>) => Promise<void>;
}

export function CustomerForm({ open, customer, onClose, onSave }: CustomerFormProps) {
  const [name, setName] = useState('');
  const [company, setCompany] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [gstNumber, setGstNumber] = useState('');
  const [city, setCity] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (customer) {
      setName(customer.name);
      setCompany(customer.company);
      setEmail(customer.email);
      setPhone(customer.phone);
      setGstNumber(customer.gstNumber);
      setCity(customer.city);
      setError('');
    } else {
      setName('');
      setCompany('');
      setEmail('');
      setPhone('');
      setGstNumber('');
      setCity('');
      setError('');
    }
  }, [customer, open]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError('');
    setSubmitting(true);

    const trimmedName = name.trim();
    const trimmedPhone = phone.trim();
    if (!trimmedName && !trimmedPhone) {
      setError('Enter a customer name or phone number.');
      setSubmitting(false);
      return;
    }

    try {
      await onSave({
        name: trimmedName,
        company: company.trim(),
        email: email.trim(),
        phone: trimmedPhone,
        gstNumber: gstNumber.trim(),
        city: city.trim(),
      });
      onClose();
    } catch (err) {
      setError(getApiErrorMessage(err, 'Unable to save this customer. Please try again.'));
    } finally {
      setSubmitting(false);
    }
  }

  if (!open) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-slate-950/50 px-4 py-6">
      <div className="w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-3xl bg-white p-6 shadow-2xl shadow-slate-900/10">
        <div className="mb-4 flex items-center justify-between gap-4">
          <div>
            <h2 className="text-xl font-semibold text-slate-900">
              {customer ? 'Edit Customer' : 'Add Customer'}
            </h2>
            <p className="text-sm text-slate-500">Enter customer details to {customer ? 'update' : 'create'} the record.</p>
            <p className="mt-1 text-sm text-slate-500">Customer name or phone number is required. All other fields are optional.</p>
          </div>
          <Button type="button" variant="ghost" onClick={onClose}>
            Close
          </Button>
        </div>
        <form onSubmit={handleSubmit} className="grid gap-4 sm:grid-cols-2">
          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Name</span>
            <Input value={name} onChange={(event) => setName(event.target.value)} />
          </label>
          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Company</span>
            <Input value={company} onChange={(event) => setCompany(event.target.value)} />
          </label>
          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Email</span>
            <Input value={email} onChange={(event) => setEmail(event.target.value)} type="email" />
          </label>
          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">Phone</span>
            <Input value={phone} onChange={(event) => setPhone(event.target.value)} type="tel" />
          </label>
          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">GST Number</span>
            <Input value={gstNumber} onChange={(event) => setGstNumber(event.target.value)} />
          </label>
          <label className="space-y-2">
            <span className="text-sm font-medium text-slate-700">City</span>
            <Input value={city} onChange={(event) => setCity(event.target.value)} />
          </label>
          {error && (
            <div className="sm:col-span-2 rounded-3xl bg-red-50 px-4 py-3 text-sm text-red-700">
              {error}
            </div>
          )}
          <div className="sm:col-span-2 flex flex-col gap-3 sm:flex-row sm:justify-end">
            <Button type="button" variant="secondary" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={submitting}>
              {submitting ? 'Saving...' : customer ? 'Update customer' : 'Create customer'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
