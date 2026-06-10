import { LogOut } from 'lucide-react';
import { NotificationBell } from '../notifications/NotificationBell';
import { logout } from '../../lib/auth';

interface HeaderProps {
  unreadCount?: number;
  onNotificationOpen?: () => void;
}

export function Header({ unreadCount, onNotificationOpen }: HeaderProps) {
  return (
    <header className="mb-6 flex flex-col gap-4 rounded-3xl bg-white p-4 shadow-sm shadow-slate-200/50 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 className="text-lg font-semibold text-slate-900">Welcome back</h1>
        <p className="text-sm text-slate-500">Manage your fleet operations and profit analytics.</p>
      </div>
      <div className="flex items-center gap-3">
        {onNotificationOpen ? (
          <NotificationBell unreadCount={unreadCount ?? 0} onOpen={onNotificationOpen} />
        ) : null}
        <button
          onClick={() => {
            logout();
          }}
          className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
        >
          <LogOut className="h-4 w-4" />
          Sign out
        </button>
      </div>
    </header>
  );
}
