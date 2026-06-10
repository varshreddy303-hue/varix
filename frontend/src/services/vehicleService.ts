import api from '../lib/api';
import { camelToSnake, mapVehicleRequest, mapVehicleAvailabilityResponse, mapVehicleResponse } from '../lib/transformers';
import type { Vehicle, VehicleAvailability } from '../types';

export type VehicleCreatePayload = Omit<Vehicle, 'id'>;
export type VehicleUpdatePayload = Partial<Omit<Vehicle, 'id'>>;

export async function fetchVehicles(params?: Record<string, unknown>) {
  const response = await api.get('/vehicles', {
    params: params ? camelToSnake(params) : undefined,
  });
  return (response.data as Array<Record<string, unknown>>).map(mapVehicleResponse);
}

export async function fetchVehicle(vehicleId: string) {
  const response = await api.get(`/vehicles/${vehicleId}`);
  return mapVehicleResponse(response.data as Record<string, unknown>);
}

export async function createVehicle(payload: VehicleCreatePayload) {
  const response = await api.post('/vehicles', mapVehicleRequest(payload));
  return mapVehicleResponse(response.data as Record<string, unknown>);
}

export async function updateVehicle(vehicleId: string, payload: VehicleUpdatePayload) {
  const response = await api.put(`/vehicles/${vehicleId}`, mapVehicleRequest(payload as Record<string, unknown>));
  return mapVehicleResponse(response.data as Record<string, unknown>);
}

export async function deleteVehicle(vehicleId: string) {
  await api.delete(`/vehicles/${vehicleId}`);
  return null;
}

export async function fetchVehicleAvailability(params: Record<string, unknown>) {
  const response = await api.get('/vehicles/availability', {
    params: params ? camelToSnake(params) : undefined,
  });
  return mapVehicleAvailabilityResponse(response.data as Record<string, unknown>) as VehicleAvailability;
}
