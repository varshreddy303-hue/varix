import { useCallback, useEffect, useState } from 'react';
import { ArrowUpRight, CalendarDays, DollarSign, FilePieChart, ListChecks, Users } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Header } from '../components/layout/Header';
import { NotificationCenter } from '../components/notifications/NotificationCenter';
import type { Reminder } from '../types/notifications';
import type {
  ReminderCategoryFilter,
  ReminderPriorityFilter,
  ReminderStatusFilter,
} from '../components/notifications/ReminderFilters';
import {
  archiveReminder,
  fetchReminders,
  fetchUnreadCount,
  markReminderRead,
} from '../services/reminderService';
import { useDashboard } from '../hooks/useDashboard';

function formatCurrency(amount: number) {
  return `₹${amount.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
}

function formatDate(dateString: string) {
  return new Date(dateString).toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

function statusClass(status: 'valid' | 'warning' | 'expired') {
  if (status === 'expired') return 'bg-red-100 text-red-700';
  if (status === 'warning') return 'bg-amber-100 text-amber-700';
  return 'bg-emerald-100 text-emerald-700';
}

function normalizeStatus(status: ReminderStatusFilter) {
  if (status === 'Pending') return 'pending';
  if (status === 'Read') return 'read';
  if (status === 'Archived') return 'archived';
  return undefined;
}

export function Dashboard() {
  const { data, loading, error, refresh } = useDashboard();
  const [notificationOpen, setNotificationOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [status, setStatus] = useState<ReminderStatusFilter>('All');
  const [category, setCategory] = useState<ReminderCategoryFilter>('All');
  const [priority, setPriority] = useState<ReminderPriorityFilter>('All');
  const [search, setSearch] = useState('');
  const [loadingReminders, setLoadingReminders] = useState(false);
  const [reminderError, setReminderError] = useState<string | null>(null);

  const loadUnreadCount = useCallback(async () => {
    try {
      const count = await fetchUnreadCount();
      setUnreadCount(count);
    } catch {
      setUnreadCount(0);
    }
  }, []);

  const loadReminders = useCallback(async () => {
    setLoadingReminders(true);
    setReminderError(null);

    try {
      const params = {
        status: normalizeStatus(status),
        category: category === 'All' ? undefined : category,
        search: search || undefined,
        limit: 20,
        offset: 0,
      };

      const results = await fetchReminders(params);
      const filtered = results.filter((reminder) => {
        if (priority === 'All') return true;
        const eventType = reminder.payload?.event_type ?? '';
        const priorityMap: Record<string, ReminderPriorityFilter> = {
          invoice_overdue: 'Critical',
          emi_overdue: 'Critical',
          loan_closure: 'Critical',
          trip_delayed: 'High',
          invoice_due: 'High',
          insurance_expiry: 'High',
          permit_expiry: 'High',
          fc_expiry: 'High',
          road_tax_expiry: 'High',
          pollution_expiry: 'Medium',
          gps_subscription_expiry: 'Medium',
          service_due: 'Medium',
          tyre_change_due: 'Medium',
          battery_change_due: 'Medium',
          payment_pending: 'Medium',
          trip_start_today: 'Low',
          trip_start_tomorrow: 'Low',
          driver_not_assigned: 'Low',
          vehicle_not_assigned: 'Low',
        };

        return priorityMap[eventType] === priority;
      });

      setReminders(filtered);
    } catch {
      setReminderError('Unable to load reminders.');
    } finally {
      setLoadingReminders(false);
    }
  }, [category, priority, search, status]);

  const openNotifications = useCallback(() => {
    setNotificationOpen(true);
    void loadReminders();
  }, [loadReminders]);

  const closeNotifications = () => {
    setNotificationOpen(false);
  };

  const handleMarkRead = async (id: number) => {
    try {
      await markReminderRead(id);
      setReminders((prev) => prev.map((reminder) => (reminder.id === id ? { ...reminder, status: 'read' } : reminder)));
      await loadUnreadCount();
    } catch {
      setReminderError('Failed to mark reminder as read.');
    }
  };

  const handleArchive = async (id: number) => {
    try {
      await archiveReminder(id);
      setReminders((prev) => prev.map((reminder) => (reminder.id === id ? { ...reminder, status: 'archived' } : reminder)));
      await loadUnreadCount();
    } catch {
      setReminderError('Failed to archive reminder.');
    }
  };

  useEffect(() => {
    void loadUnreadCount();
  }, [loadUnreadCount]);

  useEffect(() => {
    if (!notificationOpen) return;
    void loadReminders();
  }, [notificationOpen, loadReminders]);

  const cards = data
    ? [
        {
          title: 'Total Customers',
          value: data.totalCustomers,
          icon: Users,
        },
        {
          title: 'Total Vehicles',
          value: data.totalVehicles,
          icon: ListChecks,
        },
        {
          title: 'Active Bookings',
          value: data.activeBookings,
          icon: CalendarDays,
        },
        {
          title: 'Total Revenue',
          value: formatCurrency(data.totalRevenue),
          icon: DollarSign,
        },
        {
          title: 'Total Expenses',
          value: formatCurrency(data.totalExpenses),
          icon: FilePieChart,
        },
        {
          title: 'Total Profit',
          value: formatCurrency(data.totalProfit),
          icon: ArrowUpRight,
        },
      ]
    : [];

  return (
    <div className="space-y-6">
      <Header unreadCount={unreadCount} onNotificationOpen={openNotifications} />

      <div className="rounded-3xl bg-white p-6 shadow-sm shadow-slate-200/80">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.16em] text-slate-500">Fleet overview</p>
            <h1 className="mt-2 text-3xl font-semibold text-slate-900">Welcome back to VahanOne</h1>
            <p className="mt-2 max-w-2xl text-sm text-slate-600">
              Monitor your fleet performance, renewals, bookings, and profitability from a single dashboard.
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <Button onClick={refresh} disabled={loading}>
              {loading ? 'Refreshing...' : 'Refresh metrics'}
            </Button>
            <Button variant="secondary" onClick={openNotifications}>
              Open notifications
            </Button>
          </div>
        </div>
      </div>

      {error && (
        <Card className="rounded-3xl bg-red-50 text-red-700">
          <div className="flex flex-col gap-2">
            <p className="font-semibold">Unable to load dashboard data</p>
            <p className="text-sm">{error}</p>
          </div>
        </Card>
      )}

      {loading && !data ? (
        <div className="grid gap-4 xl:grid-cols-3">
          {[...Array(6)].map((_, index) => (
            <div key={index} className="h-36 animate-pulse rounded-3xl bg-slate-100" />
          ))}
        </div>
      ) : (
        <div className="grid gap-4 lg:grid-cols-3">
          {cards.map((card) => {
            const Icon = card.icon;
            return (
              <Card key={card.title} className="rounded-3xl border border-slate-200 p-6">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <p className="text-sm font-medium uppercase tracking-[0.16em] text-slate-500">{card.title}</p>
                    <p className="mt-4 text-3xl font-semibold text-slate-900">{card.value}</p>
                  </div>
                  <div className="flex h-12 w-12 items-center justify-center rounded-3xl bg-slate-100 text-slate-700">
                    <Icon className="h-5 w-5" />
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      )}

      <div className="grid gap-4 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="grid gap-4">
          <Card className="rounded-3xl p-6">
            <div className="mb-4 flex items-center justify-between gap-4">
              <div>
                <h2 className="text-xl font-semibold text-slate-900">Upcoming Renewals</h2>
                <p className="text-sm text-slate-500">Track the next compliance items that need attention.</p>
              </div>
              <Input placeholder="Search renewals" disabled />
            </div>

            {data?.upcomingRenewals.length ? (
              <div className="space-y-4">
                {data.upcomingRenewals.map((renewal) => (
                  <div key={`${renewal.vehicleId}-${renewal.type}`} className="rounded-3xl border border-slate-200 p-4 shadow-sm shadow-slate-100">
                    <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                      <div>
                        <p className="font-semibold text-slate-900">{renewal.licensePlate}</p>
                        <p className="text-sm text-slate-500">{renewal.type} expires on {formatDate(renewal.expiryDate)}</p>
                      </div>
                      <span className={`rounded-full px-3 py-1 text-xs font-semibold ${statusClass(renewal.status)}`}>
                        {renewal.status === 'expired' ? 'Expired' : renewal.status === 'warning' ? 'Expiring soon' : 'Valid'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="rounded-3xl border border-dashed border-slate-200 bg-slate-50 p-8 text-center text-slate-500">
                <p className="text-base font-medium text-slate-900">No renewals due soon</p>
                <p className="mt-2 text-sm">Your fleet compliance looks healthy for the next 30 days.</p>
              </div>
            )}
          </Card>

          <Card className="rounded-3xl p-6">
            <div className="mb-4 flex items-center justify-between gap-4">
              <div>
                <h2 className="text-xl font-semibold text-slate-900">Recent Bookings</h2>
                <p className="text-sm text-slate-500">Latest reservations from your fleet schedule.</p>
              </div>
              <Button variant="secondary">View all</Button>
            </div>

            {data?.recentBookings.length ? (
              <div className="space-y-4">
                {data.recentBookings.map((booking) => (
                  <div key={booking.id} className="rounded-3xl border border-slate-200 p-4 shadow-sm shadow-slate-100">
                    <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                      <div>
                        <p className="font-semibold text-slate-900">{booking.customerName}</p>
                        <p className="text-sm text-slate-500">{booking.vehicleLabel}</p>
                      </div>
                      <div className="text-right text-sm text-slate-500">
                        <p>{formatDate(booking.startDate)} → {formatDate(booking.endDate)}</p>
                        <p className="mt-1 text-slate-700">{booking.status}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="rounded-3xl border border-dashed border-slate-200 bg-slate-50 p-8 text-center text-slate-500">
                <p className="text-base font-medium text-slate-900">No recent bookings</p>
                <p className="mt-2 text-sm">Bookings will appear here once the fleet starts moving.</p>
              </div>
            )}
          </Card>
        </div>

        <Card className="rounded-3xl p-6">
          <div className="mb-4 flex items-center justify-between gap-4">
            <div>
              <h2 className="text-xl font-semibold text-slate-900">Top Profitable Vehicles</h2>
              <p className="text-sm text-slate-500">Highest revenue vehicles from recent operations.</p>
            </div>
            <Button variant="secondary">Analytics</Button>
          </div>

          {data?.topProfitableVehicles.length ? (
            <div className="space-y-4">
              {data.topProfitableVehicles.map((vehicle) => (
                <div key={vehicle.vehicleId} className="rounded-3xl border border-slate-200 p-4 shadow-sm shadow-slate-100">
                  <div className="flex items-center justify-between gap-4">
                    <div>
                      <p className="font-semibold text-slate-900">{vehicle.licensePlate}</p>
                      <p className="text-sm text-slate-500">Revenue: {formatCurrency(vehicle.revenue)}</p>
                    </div>
                    <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
                      Top performer
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="rounded-3xl border border-dashed border-slate-200 bg-slate-50 p-8 text-center text-slate-500">
              <p className="text-base font-medium text-slate-900">No profitability data yet</p>
              <p className="mt-2 text-sm">Vehicle revenue will populate here once trips and bookings are recorded.</p>
            </div>
          )}
        </Card>
      </div>

      <NotificationCenter
        open={notificationOpen}
        unreadCount={unreadCount}
        reminders={reminders}
        status={status}
        category={category}
        priority={priority}
        search={search}
        loading={loadingReminders}
        error={reminderError}
        onClose={closeNotifications}
        onStatusChange={setStatus}
        onCategoryChange={setCategory}
        onPriorityChange={setPriority}
        onSearchChange={setSearch}
        onMarkRead={handleMarkRead}
        onArchive={handleArchive}
      />
    </div>
  );
}
