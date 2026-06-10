import { Search } from 'lucide-react';
import { Input } from '../ui/Input';

const categories = ['All', 'Vehicle Compliance', 'Finance', 'Operations', 'Payments'] as const;
const priorities = ['All', 'Critical', 'High', 'Medium', 'Low'] as const;
const statuses = ['All', 'Pending', 'Read', 'Archived'] as const;

type ReminderCategoryFilter = (typeof categories)[number];
type ReminderPriorityFilter = (typeof priorities)[number];
type ReminderStatusFilter = (typeof statuses)[number];

interface ReminderFiltersProps {
  category: ReminderCategoryFilter;
  priority: ReminderPriorityFilter;
  status: ReminderStatusFilter;
  search: string;
  onCategoryChange: (value: ReminderCategoryFilter) => void;
  onPriorityChange: (value: ReminderPriorityFilter) => void;
  onStatusChange: (value: ReminderStatusFilter) => void;
  onSearchChange: (value: string) => void;
}

export function ReminderFilters({
  category,
  priority,
  status,
  search,
  onCategoryChange,
  onPriorityChange,
  onStatusChange,
  onSearchChange,
}: ReminderFiltersProps) {
  return (
    <div className="space-y-4 border-b border-slate-200 pb-4">
      <div className="grid gap-3 sm:grid-cols-[1.7fr_1fr]">
        <Input
          value={search}
          onChange={(event) => onSearchChange(event.currentTarget.value)}
          placeholder="Search reminders"
          icon={Search}
        />
        <div className="grid gap-2 sm:grid-cols-3">
          <select
            value={status}
            onChange={(event) => onStatusChange(event.currentTarget.value as ReminderStatusFilter)}
            className="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-slate-400"
          >
            {statuses.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
          <select
            value={category}
            onChange={(event) => onCategoryChange(event.currentTarget.value as ReminderCategoryFilter)}
            className="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-slate-400"
          >
            {categories.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
          <select
            value={priority}
            onChange={(event) => onPriorityChange(event.currentTarget.value as ReminderPriorityFilter)}
            className="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-slate-400"
          >
            {priorities.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </div>
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-slate-600">
          Refine your notifications
        </span>
        <span className="text-sm text-slate-500">
          Use filters to find critical alerts, renewals, or overdue invoices quickly.
        </span>
      </div>
    </div>
  );
}

export type { ReminderCategoryFilter, ReminderPriorityFilter, ReminderStatusFilter };
