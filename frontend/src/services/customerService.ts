import api from '../lib/api';
import { camelToSnake, mapCustomerRequest, mapCustomerResponse } from '../lib/transformers';
import type { Customer } from '../types';

export type CustomerCreatePayload = Omit<Customer, 'id'>;
export type CustomerUpdatePayload = Partial<Omit<Customer, 'id'>>;

export async function fetchCustomers(params?: Record<string, unknown>) {
  const response = await api.get('/customers', {
    params: params ? camelToSnake(params) : undefined,
  });
  return (response.data as Array<Record<string, unknown>>).map(mapCustomerResponse);
}

export async function fetchCustomer(customerId: string) {
  const response = await api.get(`/customers/${customerId}`);
  return mapCustomerResponse(response.data as Record<string, unknown>);
}

export async function createCustomer(payload: CustomerCreatePayload) {
  const response = await api.post('/customers', mapCustomerRequest(payload));
  return mapCustomerResponse(response.data as Record<string, unknown>);
}

export async function updateCustomer(customerId: string, payload: CustomerUpdatePayload) {
  const response = await api.put(`/customers/${customerId}`, mapCustomerRequest(payload as Record<string, unknown>));
  return mapCustomerResponse(response.data as Record<string, unknown>);
}

export async function deleteCustomer(customerId: string) {
  await api.delete(`/customers/${customerId}`);
  return null;
}
