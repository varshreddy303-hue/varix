import api from '../lib/api';
import { camelToSnake, mapTripRequest, mapTripResponse } from '../lib/transformers';
import type { Trip } from '../types';

export type TripCreatePayload = Omit<Trip, 'id' | 'distanceKm'>;
export type TripUpdatePayload = Partial<Omit<Trip, 'id'>>;

export async function fetchTrips(params?: Record<string, unknown>) {
  const response = await api.get('/trips', {
    params: params ? camelToSnake(params) : undefined,
  });
  return (response.data as Array<Record<string, unknown>>).map(mapTripResponse);
}

export async function fetchTrip(tripId: string) {
  const response = await api.get(`/trips/${tripId}`);
  return mapTripResponse(response.data as Record<string, unknown>);
}

export async function createTrip(payload: TripCreatePayload) {
  const response = await api.post('/trips', mapTripRequest(payload as Record<string, unknown>));
  return mapTripResponse(response.data as Record<string, unknown>);
}

export async function updateTrip(tripId: string, payload: TripUpdatePayload) {
  const response = await api.put(`/trips/${tripId}`, mapTripRequest(payload as Record<string, unknown>));
  return mapTripResponse(response.data as Record<string, unknown>);
}

export async function deleteTrip(tripId: string) {
  await api.delete(`/trips/${tripId}`);
  return null;
}
