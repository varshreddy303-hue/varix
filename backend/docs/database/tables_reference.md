# VahanOne — Tables Reference

This file provides a concise reference for each table: purpose, columns, types, constraints, indexes, and relationships.

---

## organizations
- Purpose: tenant/organization metadata and plan info.
- Columns:
  - `id` — UUID PK
  - `name` — varchar(255), unique
  - `plan` — varchar(100)
  - `is_active` — boolean
  - `created_at`, `updated_at`
- Constraints: `name` unique
- Indexes: PK on `id`
- Relationships: referenced by most domain tables via `organization_id`.

---

## users
- Purpose: application users (tenant-scoped or platform admins).
- Columns:
  - `id` UUID PK
  - `organization_id` UUID FK -> `organizations.id` (nullable for platform admins)
  - `email`, `hashed_password`, `is_active`, `is_superuser`
  - `created_at`, `updated_at`
- Constraints: UNIQUE(organization_id, email)
- Indexes: `organization_id` index
- Relationships: many-to-one to `organizations`; many-to-many to `roles` via `user_roles`.

---

## roles, permissions, role_permissions, user_roles
- Purpose: RBAC model (roles and permissions mapping; user-role assignments).
- Columns & constraints: standard mapping tables with foreign keys to `roles` and `permissions`.

---

## customers
- Purpose: tenant customers / clients
- Columns (high level): `id` BIGINT PK, `organization_id` UUID, `customer_name`, `phone_number`, `email`, `gst_number`, `address`, `city`, `state`, `pincode`, `created_at`, `updated_at`, `deleted_at`
- Constraints:
  - UNIQUE(organization_id, phone_number)
  - UNIQUE(organization_id, gst_number)
- Indexes:
  - `ix_customers_org_phone` (organization_id, phone_number)
  - `ix_customers_org_gst` (organization_id, gst_number)
  - add trigram/GIN on `customer_name` for full-text search (recommendation)
- Relationships: bookings (1->N), invoices (1->N)

---

## vehicles
- Purpose: fleet asset master
- Columns: `id`, `organization_id`, `vehicle_number`, `vehicle_type`, `model`, `registration_expiry`, `insurance_expiry`, timestamps
- Constraints: UNIQUE(organization_id, vehicle_number)
- Indexes: org+vehicle_number
- Relationships: bookings, expenses, maintenance records (future)

---

## drivers
- Purpose: driver master
- Columns: `id`, `organization_id`, `name`, `license_number`, `license_expiry`, `contact_number`, timestamps
- Constraints: UNIQUE(organization_id, license_number)
- Indexes: org+license_number
- Relationships: bookings, trips, expenses

---

## bookings
- Purpose: booking requests / orders
- Columns: `id`, `organization_id`, `customer_id`, `vehicle_id` (nullable), `driver_id` (nullable), `status`, `scheduled_from`, `scheduled_to`, `metadata`, timestamps
- Constraints: FK to `customers`, optional FK to `vehicles`/`drivers`
- Indexes: org+customer, org+scheduled_from
- Relationships: one-to-one optional `trip`; many-to-one `customer`

---

## trips
- Purpose: executed booking records
- Columns: `id`, `organization_id`, `booking_id`, `start_time`, `end_time`, `distance_km`, `fare`, `telemetry` JSONB, timestamps
- Constraints: booking_id -> bookings.id (unique relationship)
- Indexes: org+start_time
- Relationships: booking (1:1)

---

## expenses
- Purpose: vehicle/driver/trip expenses
- Columns: `id`, `organization_id`, `vehicle_id`, `driver_id`, `trip_id`, `amount_cents`, `currency`, `category`, `metadata`, timestamps
- Indexes: org+vehicle
- Relationships: optional FK to vehicles/drivers/trips

---

## invoices
- Purpose: billing; invoice per booking/trip or batch
- Columns: `id`, `organization_id`, `customer_id`, `amount_cents`, `amount_paid_cents`, `due_date`, `status`, `metadata`, timestamps
- Indexes: org+customer
- Relationships: payments (1:N)

---

## payments
- Purpose: payments against invoices
- Columns: `id`, `organization_id`, `invoice_id`, `amount_cents`, `method`, `transaction_ref`, `status`, timestamps
- Indexes: org+invoice
- Relationships: invoice (many-to-one); payment_reconciliation (1->N)

---

## payment_reconciliation
- Purpose: reconcile incoming payments against invoices and variance tracking
- Columns: `id`, `organization_id`, `payment_id`, `invoice_id`, `reconciliation_status`, `reconciled_amount_cents`, `variance_cents`, `reconciled_at`, `reconciled_by_user_id`, `created_at`
- Indexes: org+payment_id, reconciliation_status
- Relationships: payment (many-to-one), invoice (optional many-to-one)

---

## vehicle_daily_profit
- Purpose: daily profitability snapshots per vehicle
- Columns: `id`, `organization_id`, `vehicle_id`, `report_date`, `revenue_cents`, `expense_cents`, `profit_cents`, `trip_count`, `distance_km`, `notes`, timestamps
- Indexes: org+vehicle_id+report_date
- Relationships: vehicle (many-to-one)

---

## vehicle_monthly_profit
- Purpose: monthly profitability snapshots per vehicle
- Columns: `id`, `organization_id`, `vehicle_id`, `period_start`, `revenue_cents`, `expense_cents`, `profit_cents`, `trip_count`, `distance_km`, `notes`, timestamps
- Indexes: org+vehicle_id+period_start
- Relationships: vehicle (many-to-one)

---

## ledger_entries
- Purpose: accounting ledger entries for profitability, cash flow, and reconciliation
- Columns: `id`, `organization_id`, `entry_date`, `account_code`, `description`, `amount_cents`, `currency`, `entry_type`, `vehicle_id`, `trip_id`, `invoice_id`, `payment_id`, `metadata`, timestamps
- Indexes: org+vehicle_id, org+entry_date
- Relationships: vehicle (optional many-to-one), trip (optional many-to-one), invoice (optional many-to-one), payment (optional many-to-one)

---

## document_renewals
- Purpose: store expiry reminders for vehicle/driver documents
- Columns: `id`, `organization_id`, `subject_type`, `subject_id`, `document_type`, `expiry_date`, `metadata`, timestamps
- Indexes: org+expiry_date

---

## notifications
- Purpose: tenant notifications (email, sms, webhooks)
- Columns: `id`, `organization_id`, `recipient_id`, `channel`, `payload`, `scheduled_time`, `sent_at`, `status`, timestamps
- Indexes: org+scheduled_time

---

## attachments
- Purpose: metadata for files stored in S3
- Columns: `id`, `organization_id`, `object_type`, `object_id`, `storage_path`, `mime_type`, `checksum`, timestamps
- Indexes: org+object_type+object_id

---

## audit_logs
- Purpose: append-only audit record for critical actions
- Columns: `id`, `organization_id`, `user_id`, `entity_type`, `entity_id`, `action`, `changes` JSONB, `created_at`
- Indexes: org+created_at
