import { useState } from 'react';
import { Archive, CheckCircle2, ChevronDown, ChevronUp, Info } from 'lucide-react';
import { getReminderCategory, getReminderPriority, formatReminderDate } from '../../types/notifications';
import type { ReminderPriority, ReminderStatus } from '../../types/notifications';

interface ReminderCardProps {
  reminder: {
    id: number;
    message: string;
    status: ReminderStatus;
    reminder_date: string;
    due_date: string | null;
    entity_type: string | null;
    payload: Record<string, any> | null;
  };
  onMarkRead: (id: number) => void;
  onArchive: (id: number) => void;
}

const priorityStyles: Record<ReminderPriority, string> = {
  Critical: 'bg-rose-100 text-rose-700',
  High: 'bg-amber-100 text-amber-800',
  Medium: 'bg-sky-100 text-sky-700',
  Low: 'bg-slate-100 text-slate-700',
};

const statusStyles: Record<ReminderStatus, string> = {
  pending: 'bg-amber-100 text-amber-800',
  read: 'bg-emerald-100 text-emerald-700',
  archived: 'bg-slate-100 text-slate-500',
};

export function ReminderCard({ reminder, onMarkRead, onArchive }: ReminderCardProps) {
  const [expanded, setExpanded] = useState(false);
  const eventCategory = getReminderCategory(reminder.payload?.event_type ?? '');
  const priority = getReminderPriority(reminder.payload?.event_type ?? '');

  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm shadow-slate-100">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            <span className={`rounded-full px-3 py-1 text-xs font-semibold ${priorityStyles[priority]}`}>
              {priority}
            </span>
            <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-slate-600">
              {eventCategory}
            </span>
            <span className={`rounded-full px-3 py-1 text-xs font-semibold ${statusStyles[reminder.status]}`}>
              {reminder.status === 'pending' ? 'Unread' : reminder.status === 'read' ? 'Read' : 'Archived'}
            </span>
          </div>
          <div>
            <p className="text-sm font-semibold text-slate-900">{reminder.message}</p>
            <p className="mt-1 text-sm text-slate-500">
              Reminder scheduled for {formatReminderDate(reminder.reminder_date)}
            </p>
          </div>
        </div>
        <div className="flex flex-col items-start gap-2 sm:items-end">
          <button
            type="button"
            onClick={() => setExpanded(!expanded)}
            className="inline-flex items-center gap-2 rounded-full bg-slate-100 px-4 py-2 text-sm text-slate-700 transition hover:bg-slate-200"
          >
            <span>{expanded ? 'Hide details' : 'Open details'}</span>
            {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </button>
          <div className="flex flex-wrap items-center gap-2">
            <button
              type="button"
              onClick={() => onMarkRead(reminder.id)}
              disabled={reminder.status === 'read' || reminder.status === 'archived'}
              className="inline-flex items-center gap-2 rounded-full bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-500"
            >
              <CheckCircle2 className="h-4 w-4" />
              Mark read
            </button>
            <button
              type="button"
              onClick={() => onArchive(reminder.id)}
              disabled={reminder.status === 'archived'}
              className="inline-flex items-center gap-2 rounded-full bg-slate-100 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-200 disabled:cursor-not-allowed disabled:bg-slate-50 disabled:text-slate-400"
            >
              <Archive className="h-4 w-4" />
              Archive
            </button>
          </div>
        </div>
      </div>
      {expanded && (
        <div className="mt-4 rounded-3xl border border-slate-100 bg-slate-50 p-4 text-sm text-slate-600">
          <div className="mb-3 flex items-center gap-2 text-slate-700">
            <Info className="h-4 w-4" />
            <span className="font-semibold">Details</span>
          </div>
          <div className="grid gap-2 sm:grid-cols-2">
            <div>
              <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Event type</p>
              <p className="mt-1 text-sm text-slate-900">{reminder.payload?.event_type ?? 'Unknown'}</p>
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Due date</p>
              <p className="mt-1 text-sm text-slate-900">{formatReminderDate(reminder.due_date)}</p>
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Entity</p>
              <p className="mt-1 text-sm text-slate-900">{reminder.entity_type ?? 'General'}</p>
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Source</p>
              <p className="mt-1 text-sm text-slate-900">{reminder.payload?.source_date ? formatReminderDate(reminder.payload.source_date) : 'N/A'}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
