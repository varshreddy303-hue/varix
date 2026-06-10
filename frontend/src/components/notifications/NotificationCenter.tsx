import { X } from 'lucide-react';
import { Button } from '../ui/Button';
import { ReminderCard } from './ReminderCard';
import { ReminderFilters, type ReminderCategoryFilter, type ReminderPriorityFilter, type ReminderStatusFilter } from './ReminderFilters';
import type { Reminder } from '../../types/notifications';

interface NotificationCenterProps {
  open: boolean;
  unreadCount: number;
  reminders: Reminder[];
  status: ReminderStatusFilter;
  category: ReminderCategoryFilter;
  priority: ReminderPriorityFilter;
  search: string;
  loading: boolean;
  error: string | null;
  onClose: () => void;
  onStatusChange: (value: ReminderStatusFilter) => void;
  onCategoryChange: (value: ReminderCategoryFilter) => void;
  onPriorityChange: (value: ReminderPriorityFilter) => void;
  onSearchChange: (value: string) => void;
  onMarkRead: (id: number) => void;
  onArchive: (id: number) => void;
}

export function NotificationCenter({
  open,
  unreadCount,
  reminders,
  status,
  category,
  priority,
  search,
  loading,
  error,
  onClose,
  onStatusChange,
  onCategoryChange,
  onPriorityChange,
  onSearchChange,
  onMarkRead,
  onArchive,
}: NotificationCenterProps) {
  if (!open) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/40 p-4 backdrop-blur-sm sm:p-6">
      <div className="mx-auto flex h-full max-w-6xl flex-col overflow-hidden rounded-[2rem] bg-white shadow-2xl ring-1 ring-slate-200">
        <div className="flex items-center justify-between border-b border-slate-200 px-6 py-5">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.3em] text-slate-500">Notification center</p>
            <h2 className="mt-2 text-2xl font-semibold text-slate-900">Your reminders and alerts</h2>
            <p className="mt-2 max-w-2xl text-sm text-slate-600">
              Review the latest reminders generated for your fleet and mark them read or archive them as needed.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <span className="rounded-full bg-slate-100 px-3 py-2 text-sm font-semibold text-slate-700">
              {unreadCount} unread
            </span>
            <Button variant="secondary" onClick={onClose}>
              <X className="h-4 w-4" />
              Close
            </Button>
          </div>
        </div>

        <div className="overflow-y-auto p-6">
          <ReminderFilters
            category={category}
            priority={priority}
            status={status}
            search={search}
            onCategoryChange={onCategoryChange}
            onPriorityChange={onPriorityChange}
            onStatusChange={onStatusChange}
            onSearchChange={onSearchChange}
          />

          {error ? (
            <div className="mt-6 rounded-3xl border border-red-100 bg-red-50 p-6 text-sm text-red-700">
              {error}
            </div>
          ) : null}

          {loading ? (
            <div className="mt-6 grid gap-4">
              {[...Array(3)].map((_, index) => (
                <div key={index} className="h-40 animate-pulse rounded-3xl bg-slate-100" />
              ))}
            </div>
          ) : reminders.length === 0 ? (
            <div className="mt-6 rounded-3xl border border-dashed border-slate-200 bg-slate-50 p-10 text-center text-slate-500">
              <p className="text-lg font-semibold text-slate-900">No reminders found</p>
              <p className="mt-2">Adjust your filters or refresh the notification center to see the latest alerts.</p>
            </div>
          ) : (
            <div className="mt-6 grid gap-4">
              {reminders.map((reminder) => (
                <ReminderCard
                  key={reminder.id}
                  reminder={reminder}
                  onMarkRead={onMarkRead}
                  onArchive={onArchive}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
