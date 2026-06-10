# VahanOne — Database Overview

This document provides a high-level overview of the VahanOne data model, ER relationships, business flows, cardinality, and multi-tenant strategy.

## ER Diagram (conceptual)

- `organizations` (1) — (N) `users`
- `organizations` (1) — (N) `customers`
- `organizations` (1) — (N) `vehicles`
- `organizations` (1) — (N) `drivers`
- `customers` (1) — (N) `bookings`
- `bookings` (1) — (1) `trips` (optional)
- `bookings` (1) — (N) `invoices`
- `invoices` (1) — (N) `payments`
- `vehicles`/`drivers` (1) — (N) `expenses`
- `organizations` (1) — (N) `audit_logs`, `notifications`, `attachments`

Notes: ER diagram images should be generated from the `app/db/models.py` file using a tool (dbdiagram.io, Graphviz, or ERAlchemy).

## Business Flow Summary

- A tenant (organization) owns users, customers, vehicles, drivers, and domain records.
- Customers request bookings; bookings are optionally assigned vehicles and drivers.
- Trips record executed bookings and telematics/metrics.
- Expenses are recorded against vehicles, drivers, or trips.
- Invoices are generated per booking/trip or batched; payments settle invoices.
- Audit logs record critical changes with tenant and user context.

## Foreign Keys & Referential Integrity

- All domain tables include `organization_id` FK when appropriate. Primary foreign relationships:
  - `users.organization_id -> organizations.id`
  - `customers.organization_id -> organizations.id`
  - `vehicles.organization_id -> organizations.id`
  - `drivers.organization_id -> organizations.id`
  - `bookings.customer_id -> customers.id`
  - `bookings.vehicle_id -> vehicles.id` (nullable)
  - `bookings.driver_id -> drivers.id` (nullable)
  - `trips.booking_id -> bookings.id`
  - `invoices.customer_id -> customers.id`
  - `payments.invoice_id -> invoices.id`

Refer to `tables_reference.md` for full listing and cardinality details.

## Cardinality

- Organizations own many-of relationships to users and domain objects.
- Customers can have many bookings; bookings map to zero-or-one trip.
- Vehicles and drivers can have many bookings/trips; many-to-many assignment (if required) is modeled via assignment tables in future.

## Multi-tenant Strategy

Primary strategy: logical multi-tenancy using a single database and tenant-scoped rows via `organization_id`.

Key controls:
- Application layer: require tenant in JWT (`org`) or header `X-Organization-Id` and pass to repositories.
- DB-level: recommend Row-Level Security (RLS) policies per table and session variable `app.current_tenant` where possible.
- Partitioning: hash partition large tables by `organization_id` or range partition by `created_at` for time-series data.
- Isolation for very large tenants: dedicated databases or schemas (hybrid model).

## Notes on Scaling

- Use Kafka + Debezium for CDC to stream OLTP changes into OLAP/Data Warehouse.
- Use OpenSearch for name/phone/GST full-text and faceted search.
- Use Redis for caching and rate-limiting.
