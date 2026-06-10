import api from '../lib/api';
import { camelToSnake, mapProfitSummaryResponse, mapTripProfitResponse, mapVehicleDailyProfitResponse, mapVehicleMonthlyProfitResponse } from '../lib/transformers';
import type {
  ProfitSummary,
  TripProfit,
  VehicleDailyProfit,
  VehicleMonthlyProfit,
} from '../types';

export async function fetchProfitSummary(params?: Record<string, unknown>) {
  const response = await api.get('/profits/summary', {
    params: params ? camelToSnake(params) : undefined,
  });
  return mapProfitSummaryResponse(response.data as Record<string, unknown>) as ProfitSummary;
}

export async function fetchTripProfit(tripId: string) {
  const response = await api.get(`/profits/trip/${tripId}`);
  return mapTripProfitResponse(response.data as Record<string, unknown>) as TripProfit;
}

export async function fetchVehicleDailyProfit(vehicleId: string, params?: Record<string, unknown>) {
  const response = await api.get(`/profits/vehicle/${vehicleId}/daily`, {
    params: params ? camelToSnake(params) : undefined,
  });
  return (response.data as Array<Record<string, unknown>>).map(mapVehicleDailyProfitResponse) as VehicleDailyProfit[];
}

export async function fetchVehicleMonthlyProfit(vehicleId: string, params?: Record<string, unknown>) {
  const response = await api.get(`/profits/vehicle/${vehicleId}/monthly`, {
    params: params ? camelToSnake(params) : undefined,
  });
  return (response.data as Array<Record<string, unknown>>).map(mapVehicleMonthlyProfitResponse) as VehicleMonthlyProfit[];
}
