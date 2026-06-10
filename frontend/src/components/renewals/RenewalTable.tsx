import { ArrowDown, ArrowUp } from 'lucide-react';

export type RenewalDocumentType = 'Insurance' | 'Permit' | 'FC' | 'Pollution' | 'Road Tax';
export type RenewalStatus = 'Expired' | 'Expiring Soon' | 'Valid';

export interface RenewalRow {
  id: string;
  vehicleNumber: string;
  documentType: RenewalDocumentType;
  expiryDate: string;
  daysRemaining: number;
  status: RenewalStatus;
}

interface RenewalTableProps {
  items: RenewalRow[];
  sortDirection: 'asc' | 'desc';
  onSortChange: () => void;
}

export function RenewalTable({ items, sortDirection, onSortChange }: RenewalTableProps) {
  return (
    <div className="overflow-hidden rounded-3xl border border-slate-200">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
          <thead className="bg-slate-50 text-slate-600">
            <tr>
              <th className="px-6 py-4 font-medium">Vehicle Number</th>
              <th className="px-6 py-4 font-medium">Document Type</th>
              <th className="px-6 py-4 font-medium">Expiry Date</th>
              <th className="px-6 py-4 font-medium">Days Remaining</th>
              <th className="px-6 py-4 font-medium">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200 bg-white">
            {items.map((item) => (
              <tr key={item.id} className="hover:bg-slate-50">
                <td className="px-6 py-4 font-medium text-slate-900">{item.vehicleNumber}</td>
                <td className="px-6 py-4 text-slate-600">{item.documentType}</td>
                <td className="px-6 py-4 text-slate-600">{item.expiryDate}</td>
                <td className="px-6 py-4 text-slate-600">{item.daysRemaining}</td>
                <td className="px-6 py-4">
                  <span
                    className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${
                      item.status === 'Expired'
                        ? 'bg-red-100 text-red-700'
                        : item.status === 'Expiring Soon'
                        ? 'bg-amber-100 text-amber-700'
                        : 'bg-emerald-100 text-emerald-700'
                    }`}
                  >
                    {item.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between border-t border-slate-200 bg-slate-50 px-6 py-3 text-sm text-slate-600">
        <p>{items.length} document{items.length === 1 ? '' : 's'} shown</p>
        <button
          type="button"
          className="inline-flex items-center gap-2 text-slate-700 hover:text-slate-900"
          onClick={onSortChange}
        >
          Sort by expiry date
          {sortDirection === 'asc' ? <ArrowUp className="h-4 w-4" /> : <ArrowDown className="h-4 w-4" />}
        </button>
      </div>
    </div>
  );
}
