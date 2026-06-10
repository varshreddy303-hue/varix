import api from '../lib/api';
import { mapCalendarEventResponse } from '../lib/transformers';
import type { CalendarEvent } from '../types';

export async function fetchCalendarEvents(params?: Record<string, unknown>) {
  const response = await api.get('/calendar', {
    params,
  });
  return (response.data as Array<Record<string, unknown>>).map(mapCalendarEventResponse);
}
