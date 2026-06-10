import api from '../lib/api';
import type { Reminder } from '../types/notifications';

export interface ReminderQueryParams {
  status?: string;
  entityType?: string;
  category?: string;
  search?: string;
  limit?: number;
  offset?: number;
}

export async function fetchReminders(params?: ReminderQueryParams): Promise<Reminder[]> {
  const response = await api.get<Reminder[]>('/reminders', {
    params,
  });
  return response.data;
}

export async function fetchUnreadCount(): Promise<number> {
  const response = await api.get<{ unread_count: number }>('/reminders/unread-count');
  return response.data.unread_count;
}

export async function markReminderRead(id: number): Promise<Reminder> {
  const response = await api.post<Reminder>(`/reminders/${id}/read`);
  return response.data;
}

export async function archiveReminder(id: number): Promise<Reminder> {
  const response = await api.post<Reminder>(`/reminders/${id}/archive`);
  return response.data;
}
