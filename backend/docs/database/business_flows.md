# VahanOne — Business Flows

This document details major workflows and how domain objects flow through the system.

## Customer -> Booking -> Trip -> Invoice -> Payment -> Profit

1. Customer Creation
   - Customer is created under an `organization_id`.
   - Customer contacts and GST are validated and canonicalized.

2. Booking Creation
   - Customer requests booking via API or operator UI.
   - Booking row created with `status = pending`.
   - Availability check: vehicle/driver assignment attempted or deferred.
   - Event emitted: `booking.created`.

3. Assignment & Confirmation
   - Booking assigned to vehicle and driver; `status` moves to `confirmed`.
   - Reservation lock placed (Redis) to prevent double-assignments.

4. Trip Execution
   - When booking is executed, a `trip` row is created referencing the booking.
   - Telemetry/GPX/ODOM data stored in timeseries store (or JSONB) and linked to `trip`.
   - Event emitted: `trip.started` / `trip.completed`.

5. Expenses
   - Expenses associated with vehicle/driver/trip (fuel, tolls, maintenance).
   - Stored in `expenses` table with metadata.

6. Invoice Generation
   - On trip completion (or scheduled billing), invoice(s) generated for the booking/trip.
   - Invoice line items include trip fare and billable expenses.

7. Payment Recording
   - Payments recorded against invoice with reconciliation (transaction_ref).
   - Invoice `amount_paid_cents` updated; status moves to `paid` when fully settled.

8. Profit Calculation
   - Profit = invoice_amount - (driver_costs + vehicle costs + billable expenses + platform fees)
   - Profit calculations rely on aggregated data from trips, expenses, payroll/EMI, insurance amortization.

## Driver Lifecycle
- Driver created under org, license and expiry tracked.
- Assigned to bookings/trips; allowances and settlements recorded as expenses or payroll items.
- License renewal triggers document_renewal reminder workflows.

## Vehicle Lifecycle
- Vehicle created under org with registration and insurance expiry dates.
- Maintenance and fuel logs recorded; maintenance schedules generate reminders.
- Depreciation, EMI, and insurance tracked for financial reports.

## Notifications
- Events emit notifications through Kafka -> notification service -> delivery adapters (email/SMS/webhook).
- Notification statuses tracked in `notifications` table for retries/audit.

## Reporting
- Nightly materialized views/ETL produce summary reports (revenue, utilization, driver performance).
- Real-time dashboards use aggregated caches or read replicas to avoid OLTP load.

*** End of business flows ***