import { useEffect, useMemo, useState } from 'react';
import { Plus, Edit3, Trash2, Search } from 'lucide-react';
import { fetchCustomers, createCustomer, updateCustomer, deleteCustomer } from '../services/customerService';
import type { Customer } from '../types';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { Input } from '../components/ui/Input';
import { CustomerForm } from '../components/customers/CustomerForm';

export function Customers() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [activeCustomer, setActiveCustomer] = useState<Customer | undefined>(undefined);

  useEffect(() => {
    async function loadCustomers() {
      setLoading(true);
      setError('');
      try {
        const data = await fetchCustomers();
        setCustomers(data);
      } catch (err) {
        setError('Unable to load customers. Please refresh the page.');
      } finally {
        setLoading(false);
      }
    }

    loadCustomers();
  }, []);

  const filteredCustomers = useMemo(() => {
    const normalized = query.toLowerCase().trim();
    return customers.filter((customer) =>
      [customer.name, customer.phone, customer.email, customer.company, customer.city]
        .join(' ')
        .toLowerCase()
        .includes(normalized),
    );
  }, [customers, query]);

  async function refreshCustomers() {
    setLoading(true);
    try {
      const data = await fetchCustomers();
      setCustomers(data);
    } catch {
      setError('Unable to refresh customer list.');
    } finally {
      setLoading(false);
    }
  }

  async function handleSaveCustomer(payload: Omit<Customer, 'id'>) {
    try {
      if (activeCustomer) {
        await updateCustomer(activeCustomer.id, payload);
      } else {
        await createCustomer(payload);
      }
      await refreshCustomers();
    } catch (err) {
      throw err;
    }
  }

  async function handleDelete(customerId: string) {
    const confirmed = window.confirm('Are you sure you want to remove this customer? This action can be recovered if soft delete is supported by your backend.');
    if (!confirmed) {
      return;
    }

    setLoading(true);
    setError('');
    try {
      await deleteCustomer(customerId);
      await refreshCustomers();
    } catch {
      setError('Unable to delete customer. Please try again.');
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 rounded-3xl bg-white p-6 shadow-sm shadow-slate-200/80 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Customers</h1>
          <p className="mt-1 text-sm text-slate-600">Search, create, edit, and manage your customer accounts.</p>
        </div>
        <Button onClick={() => { setActiveCustomer(undefined); setModalOpen(true); }}>
          <Plus className="mr-2 h-4 w-4" />
          Add Customer
        </Button>
      </div>

      <Card>
        <div className="mb-6 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div className="relative w-full md:w-72">
            <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <Input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search customers"
              className="pl-11"
            />
          </div>
          <div className="text-sm text-slate-500">
            {loading ? 'Loading customers…' : `${filteredCustomers.length} customer${filteredCustomers.length === 1 ? '' : 's'} found`}
          </div>
        </div>

        {error && (
          <div className="mb-6 rounded-3xl bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        {loading ? (
          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-10 text-center text-slate-500">
            Loading customers...
          </div>
        ) : filteredCustomers.length === 0 ? (
          <div className="rounded-3xl border border-dashed border-slate-200 bg-slate-50 p-10 text-center text-slate-500">
            <p className="mb-3 text-lg font-semibold text-slate-900">No customers found</p>
            <p>Add your first customer using the button above or adjust your search.</p>
          </div>
        ) : (
          <div className="overflow-hidden rounded-3xl border border-slate-200">
            <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
              <thead className="bg-slate-50 text-slate-600">
                <tr>
                  <th className="px-6 py-4 font-medium">Name</th>
                  <th className="px-6 py-4 font-medium">Phone</th>
                  <th className="px-6 py-4 font-medium">Email</th>
                  <th className="px-6 py-4 font-medium">GST Number</th>
                  <th className="px-6 py-4 font-medium">City</th>
                  <th className="px-6 py-4 font-medium text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 bg-white">
                {filteredCustomers.map((customer) => (
                  <tr key={customer.id} className="hover:bg-slate-50">
                    <td className="px-6 py-4 font-medium text-slate-900">{customer.name}</td>
                    <td className="px-6 py-4 text-slate-600">{customer.phone}</td>
                    <td className="px-6 py-4 text-slate-600">{customer.email}</td>
                    <td className="px-6 py-4 text-slate-600">{customer.gstNumber}</td>
                    <td className="px-6 py-4 text-slate-600">{customer.city}</td>
                    <td className="px-6 py-4 text-right">
                      <div className="inline-flex items-center gap-2">
                        <Button
                          type="button"
                          variant="secondary"
                          className="inline-flex items-center gap-2"
                          onClick={() => {
                            setActiveCustomer(customer);
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
                          onClick={() => handleDelete(customer.id)}
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
        )}
      </Card>

      <CustomerForm
        open={modalOpen}
        customer={activeCustomer}
        onClose={() => setModalOpen(false)}
        onSave={handleSaveCustomer}
      />
    </div>
  );
}
