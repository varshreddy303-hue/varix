export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
}

export interface ApiResponse<T> {
  data: T;
}

export interface ProfitSummary {
  totalRevenue: number;
  totalExpense: number;
  totalProfit: number;
}

export interface TripProfit {
  tripId: string;
  vehicleId: string;
  tripRevenue: number;
  totalExpense: number;
  tripProfit: number;
  profitDate: string;
}

export interface VehicleDailyProfit {
  vehicleId: string;
  profitDate: string;
  totalRevenue: number;
  totalExpense: number;
  totalProfit: number;
}

export interface VehicleMonthlyProfit {
  vehicleId: string;
  year: number;
  month: number;
  totalRevenue: number;
  totalExpense: number;
  totalProfit: number;
}

export interface Customer {
  id: string;
  name: string;
  company: string;
  email: string;
  phone: string;
  gstNumber: string;
  city: string;
}

export interface Vehicle {
  id: string;
  vehicleType: string;
  make: string;
  model: string;
  licensePlate: string;
  seatingCapacity: number;
  fuelType: string;
  insuranceExpiry: string;
  permitExpiry: string;
  fcExpiry: string;
  pollutionExpiry: string;
  roadTaxExpiry: string;
  emiAmount: number;
  emiDueDay: number;
  status: 'active' | 'inactive';
}

export interface Booking {
  id: string;
  customerId?: string;
  customerName?: string;
  customerCompany?: string;
  customerPhone?: string;
  customerEmail?: string;
  customerGstNumber?: string;
  customerCity?: string;
  customerNotes?: string;
  vehicleId: string;
  pickupLocation: string;
  destination: string;
  startDate: string;
  endDate: string;
  amount: number;
  status: string;
}

export interface VehicleAvailability {
  vehicleId: string;
  startDate: string;
  endDate: string;
  available: boolean;
  reason?: string;
}

export type CalendarEventType = 'booking' | 'maintenance' | 'dispatch';

export interface CalendarEvent {
  id: string;
  vehicleId: string;
  title: string;
  eventType: CalendarEventType;
  status: string;
  startDate: string;
  endDate: string;
  bookingId?: string;
  maintenanceId?: string;
}

export interface MaintenanceSchedule {
  id: string;
  vehicleId: string;
  startDate: string;
  endDate: string;
  reason: string;
  status: string;
}

export interface Trip {
  id: string;
  bookingId: string;
  vehicleId: string;
  startKm: number;
  endKm: number;
  distanceKm: number;
  revenue: number;
  startTime: string;
  endTime: string;
  status: 'pending' | 'ongoing' | 'completed' | 'cancelled';
}

export type ExpenseCategory = 'fuel' | 'toll' | 'parking' | 'maintenance' | 'other';

export interface Expense {
  id: string;
  tripId?: string;
  bookingId?: string;
  vehicleId: string;
  amount: number;
  fuelAmount: number;
  tollAmount: number;
  parkingAmount: number;
  driverBataAmount: number;
  permitAmount: number;
  stateTaxAmount: number;
  foodAmount: number;
  accommodationAmount: number;
  miscAmount: number;
  totalAmount: number;
  expenseDate: string;
  paidAt?: string;
}

export type InvoiceStatus = 'Draft' | 'Sent' | 'Paid' | 'Overdue';

export interface Invoice {
  id: string;
  invoiceNumber: string;
  customerId: string;
  tripId: string;
  invoiceDate: string;
  dueDate: string;
  subtotal: number;
  taxAmount: number;
  notes: string;
  total: number;
  status: InvoiceStatus;
}
