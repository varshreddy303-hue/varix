import type { ExpenseCategory, InvoiceStatus, Trip } from '../types';

export type PlainObject = Record<string, unknown>;

function isPlainObject(value: unknown): value is PlainObject {
  return Boolean(value && typeof value === 'object' && !Array.isArray(value));
}

function toSnakeCase(key: string): string {
  return key.replace(/[A-Z]/g, (char) => `_${char.toLowerCase()}`);
}

function toCamelCase(key: string): string {
  return key.replace(/_([a-z])/g, (_, char) => char.toUpperCase());
}

export function camelToSnake<T>(value: T): unknown {
  if (Array.isArray(value)) {
    return value.map((item) => camelToSnake(item));
  }

  if (isPlainObject(value)) {
    const result: PlainObject = {};
    Object.entries(value).forEach(([key, item]) => {
      if (item === undefined) return;
      result[toSnakeCase(key)] = camelToSnake(item);
    });
    return result;
  }

  return value;
}

export function snakeToCamel<T>(value: T): unknown {
  if (Array.isArray(value)) {
    return value.map((item) => snakeToCamel(item));
  }

  if (isPlainObject(value)) {
    const result: PlainObject = {};
    Object.entries(value).forEach(([key, item]) => {
      result[toCamelCase(key)] = snakeToCamel(item);
    });
    return result;
  }

  return value;
}

export function mapCustomerRequest(payload: Record<string, unknown>) {
  const name = typeof payload.name === 'string' ? payload.name.trim() : '';
  const phone = typeof payload.phone === 'string' ? payload.phone.trim() : '';
  const email = typeof payload.email === 'string' ? payload.email.trim() : '';
  const gstNumber = typeof payload.gstNumber === 'string' ? payload.gstNumber.trim() : '';
  const city = typeof payload.city === 'string' ? payload.city.trim() : '';
  const company = typeof payload.company === 'string' ? payload.company.trim() : '';

  const result: Record<string, unknown> = {};
  if (name) result.customer_name = name;
  if (phone) result.phone_number = phone;
  if (email) result.email = email;
  if (gstNumber) result.gst_number = gstNumber;
  if (city) result.city = city;
  if (company) result.company = company;
  return result;
}

export function mapCustomerResponse(payload: Record<string, unknown>) {
  return {
    id: String(payload.id),
    name: String(payload.customer_name ?? ''),
    company: String(payload.company ?? ''),
    email: String(payload.email ?? ''),
    phone: String(payload.phone_number ?? ''),
    gstNumber: String(payload.gst_number ?? ''),
    city: String(payload.city ?? ''),
  };
}

export function mapVehicleRequest(payload: Record<string, unknown>) {
  const mapped: Record<string, unknown> = {
    vehicle_number: payload.licensePlate,
    vehicle_type: payload.vehicleType,
    make: payload.make,
    model: payload.model,
    seating_capacity: payload.seatingCapacity,
    fuel_type: payload.fuelType,
    registration_date: payload.registrationDate,
    insurance_expiry_date: payload.insuranceExpiry,
    permit_expiry_date: payload.permitExpiry,
    fc_expiry_date: payload.fcExpiry,
    pollution_expiry_date: payload.pollutionExpiry,
    road_tax_expiry_date: payload.roadTaxExpiry,
    purchase_price: payload.purchasePrice,
    emi_amount: payload.emiAmount,
    emi_due_day: payload.emiDueDay,
  };

  if (payload.status !== undefined) {
    mapped.is_active = payload.status === 'active';
  }

  return mapped;
}

export function mapVehicleResponse(payload: Record<string, unknown>) {
  return {
    id: String(payload.id),
    vehicleType: String(payload.vehicle_type ?? ''),
    make: String(payload.make ?? ''),
    model: String(payload.model ?? ''),
    licensePlate: String(payload.vehicle_number ?? ''),
    seatingCapacity: Number(payload.seating_capacity ?? 0),
    fuelType: String(payload.fuel_type ?? ''),
    insuranceExpiry: String(payload.insurance_expiry_date ?? ''),
    permitExpiry: String(payload.permit_expiry_date ?? ''),
    fcExpiry: String(payload.fc_expiry_date ?? ''),
    pollutionExpiry: String(payload.pollution_expiry_date ?? ''),
    roadTaxExpiry: String(payload.road_tax_expiry_date ?? ''),
    emiAmount: Number(payload.emi_amount ?? 0),
    emiDueDay: Number(payload.emi_due_day ?? 0),
    status: (payload.is_active === false ? 'inactive' : 'active') as 'active' | 'inactive',
  };
}

export function mapBookingRequest(payload: Record<string, unknown>) {
  return {
    customer_id: payload.customerId || undefined,
    customer_name: payload.customerName || undefined,
    customer_company: payload.customerCompany || undefined,
    customer_phone: payload.customerPhone || undefined,
    customer_email: payload.customerEmail || undefined,
    customer_gst_number: payload.customerGstNumber || undefined,
    customer_city: payload.customerCity || undefined,
    customer_notes: payload.customerNotes || undefined,
    vehicle_id: payload.vehicleId,
    pickup_location: payload.pickupLocation,
    destination: payload.destination,
    start_date: payload.startDate,
    end_date: payload.endDate,
    booking_amount: payload.amount,
    status: payload.status,
  };
}

export function mapMaintenanceRequest(payload: Record<string, unknown>) {
  return {
    vehicle_id: payload.vehicleId,
    start_date: payload.startDate,
    end_date: payload.endDate,
    reason: payload.reason,
    status: payload.status,
  };
}

export function mapMaintenanceResponse(payload: Record<string, unknown>) {
  return {
    id: String(payload.id),
    vehicleId: String(payload.vehicle_id),
    startDate: String(payload.start_date ?? ''),
    endDate: String(payload.end_date ?? ''),
    reason: String(payload.reason ?? ''),
    status: String(payload.status ?? ''),
  };
}

export function mapBookingResponse(payload: Record<string, unknown>) {
  return {
    id: String(payload.id),
    customerId: payload.customer_id ? String(payload.customer_id) : undefined,
    customerName: payload.customer_name ? String(payload.customer_name) : undefined,
    customerCompany: payload.customer_company ? String(payload.customer_company) : undefined,
    customerPhone: payload.customer_phone ? String(payload.customer_phone) : undefined,
    customerEmail: payload.customer_email ? String(payload.customer_email) : undefined,
    customerGstNumber: payload.customer_gst_number ? String(payload.customer_gst_number) : undefined,
    customerCity: payload.customer_city ? String(payload.customer_city) : undefined,
    customerNotes: payload.customer_notes ? String(payload.customer_notes) : undefined,
    vehicleId: String(payload.vehicle_id),
    pickupLocation: String(payload.pickup_location ?? ''),
    destination: String(payload.destination ?? ''),
    startDate: String(payload.start_date ?? ''),
    endDate: String(payload.end_date ?? ''),
    amount: Number(payload.booking_amount ?? 0),
    status: String(payload.status ?? ''),
  };
}

export function mapVehicleAvailabilityResponse(payload: Record<string, unknown>) {
  return {
    vehicleId: String(payload.vehicle_id),
    startDate: String(payload.start_date ?? ''),
    endDate: String(payload.end_date ?? ''),
    available: Boolean(payload.available),
    reason: payload.reason ? String(payload.reason) : undefined,
  };
}

export function mapCalendarEventResponse(payload: Record<string, unknown>) {
  return {
    id: String(payload.id),
    vehicleId: String(payload.vehicle_id),
    title: String(payload.title ?? ''),
    eventType: String(payload.event_type ?? 'booking') as 'booking' | 'maintenance' | 'dispatch',
    status: String(payload.status ?? ''),
    startDate: String(payload.start_date ?? ''),
    endDate: String(payload.end_date ?? ''),
    bookingId: payload.booking_id ? String(payload.booking_id) : undefined,
    maintenanceId: payload.maintenance_id ? String(payload.maintenance_id) : undefined,
  };
}

export function mapTripRequest(payload: Record<string, unknown>) {
  return {
    booking_id: payload.bookingId,
    vehicle_id: payload.vehicleId,
    start_km: payload.startKm,
    end_km: payload.endKm,
    trip_revenue: payload.revenue,
    start_time: payload.startTime,
    end_time: payload.endTime,
    status: payload.status,
  };
}

export function mapTripResponse(payload: Record<string, unknown>): Trip {
  const rawStatus = String(payload.status ?? 'pending');
  const status: Trip['status'] =
    rawStatus === 'ongoing'
      ? 'ongoing'
      : rawStatus === 'completed'
      ? 'completed'
      : rawStatus === 'cancelled'
      ? 'cancelled'
      : 'pending';

  return {
    id: String(payload.id),
    bookingId: String(payload.booking_id),
    vehicleId: String(payload.vehicle_id),
    startKm: Number(payload.start_km ?? 0),
    endKm: Number(payload.end_km ?? 0),
    distanceKm: Number(payload.distance_km ?? 0),
    revenue: Number(payload.trip_revenue ?? 0),
    startTime: String(payload.start_time ?? ''),
    endTime: String(payload.end_time ?? ''),
    status,
  };
}

export function mapExpenseRequest(payload: Record<string, unknown>) {
  return {
    trip_id: payload.tripId,
    vehicle_id: payload.vehicleId,
    amount: payload.amount,
    fuel_amount: payload.fuelAmount,
    toll_amount: payload.tollAmount,
    parking_amount: payload.parkingAmount,
    driver_bata_amount: payload.driverBataAmount,
    permit_amount: payload.permitAmount,
    state_tax_amount: payload.stateTaxAmount,
    food_amount: payload.foodAmount,
    accommodation_amount: payload.accommodationAmount,
    misc_amount: payload.miscAmount,
    total_amount: payload.totalAmount,
    expense_date: payload.expenseDate,
  };
}

export function mapExpenseResponse(payload: Record<string, unknown>) {
  return {
    id: String(payload.id),
    tripId: String(payload.trip_id),
    vehicleId: String(payload.vehicle_id),
    amount: Number(payload.amount ?? 0),
    fuelAmount: Number(payload.fuel_amount ?? 0),
    tollAmount: Number(payload.toll_amount ?? 0),
    parkingAmount: Number(payload.parking_amount ?? 0),
    driverBataAmount: Number(payload.driver_bata_amount ?? 0),
    permitAmount: Number(payload.permit_amount ?? 0),
    stateTaxAmount: Number(payload.state_tax_amount ?? 0),
    foodAmount: Number(payload.food_amount ?? 0),
    accommodationAmount: Number(payload.accommodation_amount ?? 0),
    miscAmount: Number(payload.misc_amount ?? 0),
    totalAmount: Number(payload.total_amount ?? 0),
    expenseDate: String(payload.expense_date ?? ''),
  };
}

export function mapInvoiceRequest(payload: Record<string, unknown>) {
  return {
    trip_id: payload.tripId,
    invoice_number: payload.invoiceNumber,
    invoice_date: payload.invoiceDate,
    due_date: payload.dueDate,
    subtotal: payload.subtotal,
    tax_amount: payload.taxAmount,
    notes: payload.notes,
  };
}

export function mapInvoiceResponse(payload: Record<string, unknown>) {
  const rawStatus = String(payload.status ?? 'draft');
  const status =
    rawStatus === 'sent'
      ? 'Sent'
      : rawStatus === 'paid'
      ? 'Paid'
      : rawStatus === 'overdue'
      ? 'Overdue'
      : 'Draft';

  return {
    id: String(payload.id),
    customerId: String(payload.customer_id),
    tripId: String(payload.trip_id),
    invoiceNumber: String(payload.invoice_number ?? ''),
    invoiceDate: String(payload.invoice_date ?? ''),
    dueDate: String(payload.due_date ?? ''),
    subtotal: Number(payload.subtotal ?? 0),
    taxAmount: Number(payload.tax_amount ?? 0),
    notes: String(payload.notes ?? ''),
    total: Number(payload.total_amount ?? 0),
    status: status as InvoiceStatus,
  };
}

export function mapProfitSummaryResponse(payload: Record<string, unknown>) {
  return {
    totalRevenue: Number(payload.total_revenue ?? 0),
    totalExpense: Number(payload.total_expense ?? 0),
    totalProfit: Number(payload.total_profit ?? 0),
  };
}

export function mapTripProfitResponse(payload: Record<string, unknown>) {
  return {
    tripId: String(payload.trip_id),
    vehicleId: String(payload.vehicle_id),
    tripRevenue: Number(payload.trip_revenue ?? 0),
    totalExpense: Number(payload.total_expense ?? 0),
    tripProfit: Number(payload.trip_profit ?? 0),
    profitDate: String(payload.profit_date ?? ''),
  };
}

export function mapVehicleDailyProfitResponse(payload: Record<string, unknown>) {
  return {
    vehicleId: String(payload.vehicle_id),
    profitDate: String(payload.profit_date ?? ''),
    totalRevenue: Number(payload.total_revenue ?? 0),
    totalExpense: Number(payload.total_expense ?? 0),
    totalProfit: Number(payload.total_profit ?? 0),
  };
}

export function mapVehicleMonthlyProfitResponse(payload: Record<string, unknown>) {
  return {
    vehicleId: String(payload.vehicle_id),
    year: Number(payload.year ?? 0),
    month: Number(payload.month ?? 0),
    totalRevenue: Number(payload.total_revenue ?? 0),
    totalExpense: Number(payload.total_expense ?? 0),
    totalProfit: Number(payload.total_profit ?? 0),
  };
}
