import api from '../lib/api';
import { camelToSnake, mapInvoiceRequest, mapInvoiceResponse } from '../lib/transformers';
import type { Invoice } from '../types';

export type InvoiceCreatePayload = Omit<Invoice, 'id' | 'status' | 'total'>;
export type InvoiceUpdatePayload = Partial<Omit<Invoice, 'id' | 'status' | 'total'>>;

export async function fetchInvoices(params?: Record<string, unknown>) {
  const response = await api.get('/invoices', {
    params: params ? camelToSnake(params) : undefined,
  });
  return (response.data as Array<Record<string, unknown>>).map(mapInvoiceResponse);
}

export async function fetchInvoice(invoiceId: string) {
  const response = await api.get(`/invoices/${invoiceId}`);
  return mapInvoiceResponse(response.data as Record<string, unknown>);
}

export async function createInvoice(payload: InvoiceCreatePayload) {
  const response = await api.post('/invoices', mapInvoiceRequest(payload));
  return mapInvoiceResponse(response.data as Record<string, unknown>);
}

export async function updateInvoice(invoiceId: string, payload: InvoiceUpdatePayload) {
  const response = await api.put(`/invoices/${invoiceId}`, mapInvoiceRequest(payload as Record<string, unknown>));
  return mapInvoiceResponse(response.data as Record<string, unknown>);
}

export async function markInvoicePaid(invoiceId: string) {
  const response = await api.post(`/invoices/${invoiceId}/mark-paid`);
  return mapInvoiceResponse(response.data as Record<string, unknown>);
}

export async function deleteInvoice(invoiceId: string) {
  await api.delete(`/invoices/${invoiceId}`);
  return null;
}
