import api from '../lib/api';
import { camelToSnake, mapMaintenanceRequest, mapMaintenanceResponse } from '../lib/transformers';
import type { MaintenanceSchedule } from '../types';

export type MaintenanceScheduleCreatePayload = Omit<MaintenanceSchedule, 'id'>;
export type MaintenanceScheduleUpdatePayload = Partial<Omit<MaintenanceSchedule, 'id'>>;

export async function fetchMaintenanceSchedules(params?: Record<string, unknown>) {
  const response = await api.get('/maintenance', {
    params: params ? camelToSnake(params) : undefined,
  });
  return (response.data as Array<Record<string, unknown>>).map(mapMaintenanceResponse);
}

export async function createMaintenanceSchedule(payload: MaintenanceScheduleCreatePayload) {
  const response = await api.post('/maintenance', mapMaintenanceRequest(payload));
  return mapMaintenanceResponse(response.data as Record<string, unknown>);
}

export async function updateMaintenanceSchedule(maintenanceId: string, payload: MaintenanceScheduleUpdatePayload) {
  const response = await api.put(`/maintenance/${maintenanceId}`, mapMaintenanceRequest(payload as Record<string, unknown>));
  return mapMaintenanceResponse(response.data as Record<string, unknown>);
}
