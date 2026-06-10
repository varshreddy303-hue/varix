import axios from 'axios';
import api, { baseURL } from '../lib/api';
import { clearAuthStorage, getRefreshToken, saveTokens } from '../lib/auth';
import type { AuthTokens } from '../types';

export interface LoginPayload {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  expires_in?: number;
}

export async function login(payload: LoginPayload) {
  const response = await api.post<AuthResponse>('/auth/login', payload);
  saveTokens({
    accessToken: response.data.access_token,
    refreshToken: response.data.refresh_token,
  });

  return response.data;
}

export async function refreshAccessToken() {
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    throw new Error('Refresh token is missing');
  }

  const response = await axios.post<AuthResponse>(
    `${baseURL}/auth/refresh`,
    { refresh_token: refreshToken },
    { headers: { 'Content-Type': 'application/json' } },
  );

  saveTokens({
    accessToken: response.data.access_token,
    refreshToken: response.data.refresh_token,
  });

  return response.data;
}

export function logout() {
  clearAuthStorage();
  window.location.href = '/login';
}
