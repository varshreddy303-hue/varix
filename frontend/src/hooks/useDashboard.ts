import { useEffect, useState } from 'react';
import type { DashboardData } from '../services/dashboardService';
import { fetchDashboardData } from '../services/dashboardService';

export function useDashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  async function loadDashboard() {
    setLoading(true);
    setError('');
    try {
      const result = await fetchDashboardData();
      setData(result);
    } catch (err) {
      setError('Unable to load dashboard metrics. Please try again later.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDashboard();
  }, []);

  return {
    data,
    loading,
    error,
    refresh: loadDashboard,
  };
}
