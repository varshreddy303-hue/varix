# VahanOne — Architecture Decisions

This document records rationale for schema and operational choices.

## Tenancy
- Decision: Single database, logical tenancy with `organization_id` plus RLS.
- Why: Operational simplicity and lower cost at scale for 100k tenants. Use hybrid approach for very large enterprise tenants.
- Tradeoffs: No strict isolation; mitigate with RLS and optional dedicated DBs for top-tier tenants.

## IDs and Types
- Organizations and Users use UUIDs for cross-system uniqueness.
- Domain entities (customers, bookings, trips) use BIGINT for efficient indexing and sequence allocation.

## Indexing
- Organization_id is included as leading column on most indexes to scope queries per tenant and improve partition pruning.
- Trigram/Gin indexes recommended for free-text search columns like `customer_name`.

## Partitioning
- Large write tables (trips, expenses, invoices) should be partitioned by hash on `organization_id` or by range (created_at) depending on query patterns.
- Partition count planning: start with 32-128 partitions and adjust.

## Audit & Compliance
- `audit_logs` is append-only; critical actions should be logged with user and tenant context.
- For compliance, consider signed/tamper-evident logs stored in immutable storage.

## Eventing & CDC
- Use Kafka for domain events and Debezium for CDC into analytics/data warehouse.
- This decouples OLTP from OLAP and supports real-time pipelines for AI/ML.

## Search
- Use OpenSearch for name/phone/GST search with near-real-time sync via Kafka.

## Telemetry/Timeseries
- High-frequency telemetry (GPS, telematics) should be stored in TimescaleDB or dedicated timeseries DB; not in JSONB on OLTP tables.

## Security
- Enforce tenant isolation in app and DB (RLS).
- Encrypt sensitive fields, use KMS, and rotate secrets regularly.

## Migrations
- Use Alembic; adopt safe migration patterns (non-blocking changes first).

## Operational
- Use pgbouncer, read replicas, and read-write split.
- Autoscale workers and consumers based on queue length and consumption lag.

*** End of architecture decisions ***