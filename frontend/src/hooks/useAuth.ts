import { useMemo } from 'react';
import { getAccessToken } from '../lib/auth';

export function useAuth() {
  const token = getAccessToken();

  return useMemo(
    () => ({
      isAuthenticated: Boolean(token),
      accessToken: token,
    }),
    [token],
  );
}
