import api from '../lib/api';
import { camelToSnake, mapBookingRequest, mapBookingResponse } from '../lib/transformers';
import type { Booking } from '../types';

export type BookingCreatePayload = Omit<Booking, 'id' | 'status'> & {
  status?: string;
};
export type BookingUpdatePayload = Partial<Omit<Booking, 'id'>>;

export async function fetchBookings(params?: Record<string, unknown>) {
  const response = await api.get('/bookings', {
    params: params ? camelToSnake(params) : undefined,
  });
  return (response.data as Array<Record<string, unknown>>).map(mapBookingResponse);
}

export async function fetchBooking(bookingId: string) {
  const response = await api.get(`/bookings/${bookingId}`);
  return mapBookingResponse(response.data as Record<string, unknown>);
}

export async function createBooking(payload: BookingCreatePayload) {
  const response = await api.post('/bookings', mapBookingRequest(payload));
  return mapBookingResponse(response.data as Record<string, unknown>);
}

export async function updateBooking(bookingId: string, payload: BookingUpdatePayload) {
  const response = await api.put(`/bookings/${bookingId}`, mapBookingRequest(payload as Record<string, unknown>));
  return mapBookingResponse(response.data as Record<string, unknown>);
}

export async function cancelBooking(bookingId: string) {
  const response = await api.post(`/bookings/${bookingId}/cancel`);
  return mapBookingResponse(response.data as Record<string, unknown>);
}
