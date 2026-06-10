export type ReminderStatus = 'pending' | 'read' | 'archived';
export type ReminderCategory = 'Vehicle Compliance' | 'Finance' | 'Operations' | 'Payments' | 'Other';
export type ReminderPriority = 'Critical' | 'High' | 'Medium' | 'Low';

export interface Reminder {
  id: number;
  rule_id: number;
  entity_type: string | null;
  entity_id: number | null;
  reminder_date: string;
  due_date: string | null;
  status: ReminderStatus;
  message: string;
  payload: Record<string, any> | null;
  organization_id: string;
  created_at: string;
  updated_at: string;
}

export const REMINDER_CATEGORY_MAP: Record<string, ReminderCategory> = {
  insurance_expiry: 'Vehicle Compliance',
  permit_expiry: 'Vehicle Compliance',
  fc_expiry: 'Vehicle Compliance',
  pollution_expiry: 'Vehicle Compliance',
  road_tax_expiry: 'Vehicle Compliance',
  gps_subscription_expiry: 'Vehicle Compliance',
  service_due: 'Vehicle Compliance',
  tyre_change_due: 'Vehicle Compliance',
  battery_change_due: 'Vehicle Compliance',
  emi_due: 'Finance',
  emi_overdue: 'Finance',
  loan_closure: 'Finance',
  invoice_due: 'Payments',
  invoice_overdue: 'Payments',
  payment_pending: 'Payments',
  trip_start_today: 'Operations',
  trip_start_tomorrow: 'Operations',
  trip_delayed: 'Operations',
  driver_not_assigned: 'Operations',
  vehicle_not_assigned: 'Operations',
};

export const REMINDER_PRIORITY_MAP: Record<string, ReminderPriority> = {
  invoice_overdue: 'Critical',
  emi_overdue: 'Critical',
  loan_closure: 'Critical',
  trip_delayed: 'High',
  invoice_due: 'High',
  insurance_expiry: 'High',
  permit_expiry: 'High',
  fc_expiry: 'High',
  road_tax_expiry: 'High',
  pollution_expiry: 'High',
  gps_subscription_expiry: 'Medium',
  service_due: 'Medium',
  tyre_change_due: 'Medium',
  battery_change_due: 'Medium',
  payment_pending: 'Medium',
  trip_start_today: 'Medium',
  trip_start_tomorrow: 'Low',
  driver_not_assigned: 'Low',
  vehicle_not_assigned: 'Low',
};

export function getReminderCategory(eventType: string): ReminderCategory {
  return REMINDER_CATEGORY_MAP[eventType] ?? 'Other';
}

export function getReminderPriority(eventType: string): ReminderPriority {
  return REMINDER_PRIORITY_MAP[eventType] ?? 'Low';
}

export function formatReminderDate(timestamp: string | null) {
  if (!timestamp) {
    return 'Unknown';
  }
  return new Date(timestamp).toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}
