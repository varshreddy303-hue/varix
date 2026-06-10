import api from '../lib/api';
import { camelToSnake, mapExpenseRequest, mapExpenseResponse } from '../lib/transformers';
import type { Expense } from '../types';

export type ExpenseCreatePayload = Omit<Expense, 'id'>;
export type ExpenseUpdatePayload = Partial<Omit<Expense, 'id'>>;

export async function fetchExpenses(params?: Record<string, unknown>) {
  const response = await api.get('/expenses', {
    params: params ? camelToSnake(params) : undefined,
  });
  return (response.data as Array<Record<string, unknown>>).map(mapExpenseResponse);
}

export async function fetchExpense(expenseId: string) {
  const response = await api.get(`/expenses/${expenseId}`);
  return mapExpenseResponse(response.data as Record<string, unknown>);
}

export async function createExpense(payload: ExpenseCreatePayload) {
  const response = await api.post('/expenses', mapExpenseRequest(payload));
  return mapExpenseResponse(response.data as Record<string, unknown>);
}

export async function updateExpense(expenseId: string, payload: ExpenseUpdatePayload) {
  const response = await api.put(`/expenses/${expenseId}`, mapExpenseRequest(payload as Record<string, unknown>));
  return mapExpenseResponse(response.data as Record<string, unknown>);
}

export async function deleteExpense(expenseId: string) {
  await api.delete(`/expenses/${expenseId}`);
  return null;
}
