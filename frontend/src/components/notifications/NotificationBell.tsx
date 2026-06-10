import { Bell } from 'lucide-react';

interface NotificationBellProps {
  unreadCount: number;
  onOpen: () => void;
}

export function NotificationBell({ unreadCount, onOpen }: NotificationBellProps) {
  return (
    <button
      type="button"
      onClick={onOpen}
      className="relative inline-flex h-11 w-11 items-center justify-center rounded-2xl border border-slate-200 bg-white text-slate-700 transition hover:bg-slate-50"
      aria-label="Open notification center"
    >
      <Bell className="h-5 w-5" />
      {unreadCount > 0 && (
        <span className="absolute -right-1 -top-1 inline-flex min-h-[18px] min-w-[18px] items-center justify-center rounded-full bg-rose-500 px-1.5 text-[11px] font-semibold text-white">
          {unreadCount > 9 ? '9+' : unreadCount}
        </span>
      )}
    </button>
  );
}
