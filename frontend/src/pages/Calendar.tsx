import { useEffect, useState } from 'react';
import { CalendarDays, Wrench, Truck } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { fetchCalendarEvents } from '../services/calendarService';
import type { CalendarEvent } from '../types';

function formatDateTime(value: string) {
  return new Date(value).toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function eventBadge(eventType: string) {
  if (eventType === 'maintenance') return 'bg-amber-100 text-amber-700';
  if (eventType === 'booking') return 'bg-sky-100 text-sky-700';
  return 'bg-slate-100 text-slate-700';
}

export function Calendar() {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError('');
      try {
        const now = new Date();
        const thirtyDaysLater = new Date(now);
        thirtyDaysLater.setDate(now.getDate() + 30);

        const results = await fetchCalendarEvents({
          start_date: now.toISOString(),
          end_date: thirtyDaysLater.toISOString(),
        });
        setEvents(results);
      } catch {
        setError('Unable to load calendar events.');
      } finally {
        setLoading(false);
      }
    }

    void load();
  }, []);

  return (
    <div className="space-y-6">
      <div className="rounded-3xl bg-white p-6 shadow-sm shadow-slate-200/80 sm:flex sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Vehicle calendar</h1>
          <p className="mt-1 text-sm text-slate-600">
            View bookings and maintenance events for the next 30 days.
          </p>
        </div>
        <Button onClick={() => window.location.reload()}>Refresh</Button>
      </div>

      {error && (
        <Card className="rounded-3xl border border-red-200 bg-red-50 p-6 text-red-700">{error}</Card>
      )}

      <div className="grid gap-4 lg:grid-cols-3">
        <Card className="rounded-3xl border border-slate-200 p-6">
          <div className="flex items-center gap-3">
            <CalendarDays className="h-5 w-5 text-slate-700" />
            <div>
              <p className="text-sm font-semibold text-slate-900">Total scheduled events</p>
              <p className="mt-1 text-3xl font-semibold text-slate-900">{events.length}</p>
            </div>
          </div>
        </Card>
        <Card className="rounded-3xl border border-slate-200 p-6">
          <div className="flex items-center gap-3">
            <Wrench className="h-5 w-5 text-slate-700" />
            <div>
              <p className="text-sm font-semibold text-slate-900">Maintenance blocks</p>
              <p className="mt-1 text-3xl font-semibold text-slate-900">{events.filter((event) => event.eventType === 'maintenance').length}</p>
            </div>
          </div>
        </Card>
        <Card className="rounded-3xl border border-slate-200 p-6">
          <div className="flex items-center gap-3">
            <Truck className="h-5 w-5 text-slate-700" />
            <div>
              <p className="text-sm font-semibold text-slate-900">Booking touchpoints</p>
              <p className="mt-1 text-3xl font-semibold text-slate-900">{events.filter((event) => event.eventType === 'booking').length}</p>
            </div>
          </div>
        </Card>
      </div>

      <Card className="rounded-3xl border border-slate-200 p-6">
        <div className="mb-6 flex items-center justify-between gap-4">
          <div>
            <h2 className="text-xl font-semibold text-slate-900">Upcoming calendar events</h2>
            <p className="text-sm text-slate-500">Events are grouped by booking and maintenance windows.</p>
          </div>
          <Button variant="secondary" onClick={() => window.location.reload()}>
            Refresh events
          </Button>
        </div>

        {loading ? (
          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-10 text-center text-slate-500">Loading events...</div>
        ) : events.length === 0 ? (
          <div className="rounded-3xl border border-dashed border-slate-200 bg-slate-50 p-10 text-center text-slate-500">
            No calendar events scheduled for the next 30 days.
          </div>
        ) : (
          <div className="space-y-4">
            {events.map((event) => (
              <div key={event.id} className="rounded-3xl border border-slate-200 bg-white p-4 shadow-sm shadow-slate-100">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <p className="text-sm text-slate-500">{event.title}</p>
                    <p className="mt-2 text-lg font-semibold text-slate-900">{formatDateTime(event.startDate)} → {formatDateTime(event.endDate)}</p>
                  </div>
                  <div className="space-y-2 text-right">
                    <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${eventBadge(event.eventType)}`}>
                      {event.eventType}
                    </span>
                    <p className="text-sm text-slate-500">Status: {event.status}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
