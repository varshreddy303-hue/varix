import { fetchBookings } from './bookingService';
import { fetchCustomers } from './customerService';
import { fetchExpenses } from './expenseService';
import { fetchProfitSummary } from './profitService';
import { fetchTrips } from './tripService';
import { fetchVehicles } from './vehicleService';
import type { Booking, Customer, Expense, ProfitSummary, Trip, Vehicle } from '../types';

export type RenewalType = 'Insurance' | 'Permit' | 'FC' | 'Pollution' | 'Road Tax';

export interface RenewalInfo {
  vehicleId: string;
  licensePlate: string;
  type: RenewalType;
  expiryDate: string;
  status: 'valid' | 'warning' | 'expired';
  daysUntilExpiry: number;
}

export interface BookingPreview {
  id: string;
  customerName: string;
  vehicleLabel: string;
  startDate: string;
  endDate: string;
  status: string;
}

export interface TopVehicleProfit {
  vehicleId: string;
  licensePlate: string;
  revenue: number;
}

export interface DashboardData {
  totalCustomers: number;
  totalVehicles: number;
  activeBookings: number;
  totalRevenue: number;
  totalExpenses: number;
  totalProfit: number;
  upcomingRenewals: RenewalInfo[];
  recentBookings: BookingPreview[];
  topProfitableVehicles: TopVehicleProfit[];
}

function getExpiryStatus(expiryDate: string) {
  const now = new Date();
  const date = new Date(expiryDate);
  const days = Math.ceil((date.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));

  if (days < 0) return { status: 'expired' as const, daysUntilExpiry: days };
  if (days <= 30) return { status: 'warning' as const, daysUntilExpiry: days };
  return { status: 'valid' as const, daysUntilExpiry: days };
}

function buildRenewals(vehicle: Vehicle) {
  const entries: RenewalInfo[] = [];
  const compliance = [
    { key: 'insuranceExpiry', label: 'Insurance' as RenewalType },
    { key: 'permitExpiry', label: 'Permit' as RenewalType },
    { key: 'fcExpiry', label: 'FC' as RenewalType },
    { key: 'pollutionExpiry', label: 'Pollution' as RenewalType },
    { key: 'roadTaxExpiry', label: 'Road Tax' as RenewalType },
  ] as const;

  compliance.forEach((item) => {
    const expiryDate = vehicle[item.key] as string;
    if (!expiryDate) return;

    const { status, daysUntilExpiry } = getExpiryStatus(expiryDate);
    if (status === 'expired' || daysUntilExpiry <= 30) {
      entries.push({
        vehicleId: vehicle.id,
        licensePlate: vehicle.licensePlate,
        type: item.label,
        expiryDate,
        status,
        daysUntilExpiry,
      });
    }
  });

  return entries;
}

function computeRevenueByVehicle(bookings: Booking[], trips: Trip[]) {
  const bookingById = new Map(bookings.map((booking) => [booking.id, booking]));
  const revenueByVehicle = new Map<string, number>();

  trips.forEach((trip) => {
    const booking = bookingById.get(trip.bookingId);
    if (!booking || !booking.vehicleId) return;
    const currentRevenue = revenueByVehicle.get(booking.vehicleId) ?? 0;
    revenueByVehicle.set(booking.vehicleId, currentRevenue + trip.revenue);
  });

  return revenueByVehicle;
}

function mapRecentBookings(bookings: Booking[], customers: Customer[], vehicles: Vehicle[]) {
  const customerById = new Map(customers.map((item) => [item.id, item]));
  const vehicleById = new Map(vehicles.map((item) => [item.id, item]));

  return bookings
    .slice()
    .sort((a, b) => Number(new Date(b.startDate)) - Number(new Date(a.startDate)))
    .slice(0, 5)
    .map((booking) => ({
      id: booking.id,
      customerName: customerById.get(booking.customerId ?? '')?.name ?? booking.customerName ?? 'Unknown customer',
      vehicleLabel: vehicleById.get(booking.vehicleId)?.licensePlate ?? booking.vehicleId,
      startDate: booking.startDate,
      endDate: booking.endDate,
      status: booking.status,
    }));
}

export async function fetchDashboardData(): Promise<DashboardData> {
  const [customers, vehicles, bookings, expenses, trips] = await Promise.all([
    fetchCustomers(),
    fetchVehicles(),
    fetchBookings(),
    fetchExpenses(),
    fetchTrips(),
  ]);

  let profitSummary: ProfitSummary | null = null;
  try {
    profitSummary = await fetchProfitSummary();
  } catch {
    profitSummary = null;
  }

  const totalRevenue = profitSummary?.totalRevenue ?? trips.reduce((sum, trip) => sum + trip.revenue, 0);
  const totalExpenses = expenses.reduce((sum, expense) => sum + expense.amount, 0);
  const totalProfit = profitSummary?.totalProfit ?? totalRevenue - totalExpenses;

  const activeBookings = bookings.filter((booking) => booking.status?.toLowerCase() === 'active').length;

  const upcomingRenewals = vehicles
    .flatMap((vehicle) => buildRenewals(vehicle))
    .sort((a, b) => a.daysUntilExpiry - b.daysUntilExpiry)
    .slice(0, 5);

  const recentBookings = mapRecentBookings(bookings, customers, vehicles);

  const revenueByVehicle = computeRevenueByVehicle(bookings, trips);
  const topProfitableVehicles = Array.from(revenueByVehicle.entries())
    .map(([vehicleId, revenue]) => ({
      vehicleId,
      licensePlate: vehicles.find((vehicle) => vehicle.id === vehicleId)?.licensePlate ?? vehicleId,
      revenue,
    }))
    .sort((a, b) => b.revenue - a.revenue)
    .slice(0, 5);

  return {
    totalCustomers: customers.length,
    totalVehicles: vehicles.length,
    activeBookings,
    totalRevenue,
    totalExpenses,
    totalProfit,
    upcomingRenewals,
    recentBookings,
    topProfitableVehicles,
  };
}
