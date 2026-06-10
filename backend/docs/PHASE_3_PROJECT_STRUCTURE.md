# VahanOne — PHASE 3: Project Structure & Architecture Blueprint

**Status:** Production-Ready Architecture Design  
**Date:** June 4, 2026  
**Scale:** 100k+ organizations · Multi-tenant SaaS

---

## COMPLETE PROJECT FOLDER STRUCTURE

```
VahanOne/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                      # FastAPI app initialization
│   │   ├── router.py                    # Main router aggregator
│   │   ├── deps.py                      # Dependency injection
│   │   │
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── routers/
│   │   │       │   ├── __init__.py
│   │   │       │   ├── auth.py          # Login, register, refresh tokens
│   │   │       │   ├── users.py         # User CRUD, profile, roles
│   │   │       │   ├── customers.py     # Customer CRUD, search, addresses
│   │   │       │   ├── vehicles.py      # Vehicle CRUD, documents, insurance
│   │   │       │   ├── drivers.py       # Driver CRUD, documents, settlements
│   │   │       │   ├── bookings.py      # Booking CRUD, status, notes
│   │   │       │   ├── trips.py         # Trip CRUD, routes, stops
│   │   │       │   ├── expenses.py      # Expense CRUD, fuel, maintenance
│   │   │       │   ├── invoices.py      # Invoice CRUD, items, taxes
│   │   │       │   ├── payments.py      # Payment CRUD, reconciliation
│   │   │       │   ├── reports.py       # Reports endpoints (revenue, utilization, profit)
│   │   │       │   ├── ai_insights.py   # AI recommendations endpoints
│   │   │       │   ├── admin.py         # Admin endpoints (org settings, users, plans)
│   │   │       │   └── health.py        # Health checks, readiness probes
│   │   │       │
│   │   │       └── responses.py         # Common response models
│   │   │
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── jwt.py                   # JWT token creation, verification
│   │   │   ├── password.py              # Password hashing, validation
│   │   │   ├── oauth.py                 # OAuth2 integration (future)
│   │   │   ├── permissions.py           # RBAC permission checking
│   │   │   └── schemas.py               # Auth request/response schemas
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py                # Pydantic settings (env vars, profiles)
│   │   │   ├── constants.py             # App constants (status enums, error codes)
│   │   │   ├── logging.py               # Structured logging setup
│   │   │   ├── exceptions.py            # Custom exception classes
│   │   │   ├── security.py              # Security utilities (encryption, key mgmt)
│   │   │   └── errors.py                # HTTP error handlers
│   │   │
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                  # SQLAlchemy declarative base
│   │   │   ├── session.py               # DB session factory, get_db()
│   │   │   ├── engine.py                # DB engine configuration
│   │   │   │
│   │   │   ├── models/                  # SQLAlchemy ORM models
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py              # Base model mixins (TimestampMixin, TenantMixin)
│   │   │   │   ├── organization.py      # Organization, Plan, TenantSettings
│   │   │   │   ├── user.py              # User, Role, Permission, ApiKey
│   │   │   │   ├── customer.py          # Customer, Address, Contact, RateCard
│   │   │   │   ├── vehicle.py           # Vehicle, Documents, Insurance, EMI, Status
│   │   │   │   ├── driver.py            # Driver, Documents, Assignment, Settlement
│   │   │   │   ├── booking.py           # Booking, StatusHistory, Notes, Attachment
│   │   │   │   ├── trip.py              # Trip, Route, Stop, Log, Expense
│   │   │   │   ├── expense.py           # Expense, FuelLog, Maintenance, Category
│   │   │   │   ├── invoice.py           # Invoice, Item, Tax, PaymentTerm
│   │   │   │   ├── payment.py           # Payment, Method, Reconciliation, Webhook
│   │   │   │   ├── audit.py             # AuditLog, ConsentRecord
│   │   │   │   ├── notification.py      # Notification, Template, Log
│   │   │   │   ├── analytics.py         # ProfitSnapshot, VehicleProfit, TripProfit
│   │   │   │   ├── ai.py                # BusinessEvent, AiInsight, AiRecommendation
│   │   │   │   └── jobs.py              # BackgroundJob, JobExecution
│   │   │   │
│   │   │   └── migrations/              # Alembic migrations
│   │   │       ├── versions/
│   │   │       └── *.py
│   │   │
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   ├── tenant.py                # Tenant context (X-Org-Id header, JWT org claim)
│   │   │   ├── auth.py                  # JWT verification, user context loading
│   │   │   ├── rls.py                   # Row-Level Security session binding
│   │   │   ├── logging.py               # Request/response logging middleware
│   │   │   ├── error_handler.py         # Global exception handler
│   │   │   ├── rate_limit.py            # Rate limiting middleware
│   │   │   └── request_id.py            # Request ID tracking for tracing
│   │   │
│   │   ├── repositories/                # Data access layer
│   │   │   ├── __init__.py
│   │   │   ├── base.py                  # Base repository with common CRUD
│   │   │   ├── customer.py              # CustomerRepository
│   │   │   ├── vehicle.py               # VehicleRepository
│   │   │   ├── driver.py                # DriverRepository
│   │   │   ├── booking.py               # BookingRepository
│   │   │   ├── trip.py                  # TripRepository
│   │   │   ├── invoice.py               # InvoiceRepository
│   │   │   ├── expense.py               # ExpenseRepository
│   │   │   ├── user.py                  # UserRepository
│   │   │   ├── audit.py                 # AuditRepository
│   │   │   └── report.py                # ReportRepository (aggregations)
│   │   │
│   │   ├── services/                    # Business logic layer
│   │   │   ├── __init__.py
│   │   │   ├── base.py                  # Base service with logging, error handling
│   │   │   ├── customer.py              # CustomerService (validation, dedup check)
│   │   │   ├── vehicle.py               # VehicleService (lifecycle, renewal tracking)
│   │   │   ├── driver.py                # DriverService (assignment, settlement)
│   │   │   ├── booking.py               # BookingService (state machine, assignment)
│   │   │   ├── trip.py                  # TripService (execution, profit calculation)
│   │   │   ├── invoice.py               # InvoiceService (generation, reconciliation)
│   │   │   ├── expense.py               # ExpenseService (categorization, approval)
│   │   │   ├── payment.py               # PaymentService (gateway integration, reconciliation)
│   │   │   ├── auth.py                  # AuthService (login, token refresh, MFA)
│   │   │   ├── user.py                  # UserService (CRUD, role assignment)
│   │   │   ├── admin.py                 # AdminService (org setup, plan management)
│   │   │   ├── notification.py          # NotificationService (email, SMS, webhooks)
│   │   │   ├── report.py                # ReportService (aggregations, queries)
│   │   │   ├── ai.py                    # AiService (insights, recommendations)
│   │   │   ├── audit.py                 # AuditService (logging, compliance)
│   │   │   └── event.py                 # EventService (Kafka publishing, domain events)
│   │   │
│   │   ├── schemas/                     # Pydantic request/response models
│   │   │   ├── __init__.py
│   │   │   ├── base.py                  # Common schemas (PaginationIn, PaginationOut)
│   │   │   ├── customer.py              # CustomerCreate, CustomerUpdate, CustomerResponse
│   │   │   ├── vehicle.py               # VehicleCreate, VehicleUpdate, etc.
│   │   │   ├── driver.py
│   │   │   ├── booking.py
│   │   │   ├── trip.py
│   │   │   ├── invoice.py
│   │   │   ├── payment.py
│   │   │   ├── user.py
│   │   │   ├── auth.py
│   │   │   ├── report.py
│   │   │   └── ai.py
│   │   │
│   │   ├── tasks/                       # Background job workers
│   │   │   ├── __init__.py
│   │   │   ├── celery_app.py            # Celery app initialization
│   │   │   ├── config.py                # Celery configuration
│   │   │   ├── notifications.py         # Tasks: send_email, send_sms, webhook_retry
│   │   │   ├── invoicing.py             # Tasks: generate_invoice, batch_billing
│   │   │   ├── reports.py               # Tasks: generate_daily_report, refresh_cache
│   │   │   ├── maintenance.py           # Tasks: check_renewals, schedule_maintenance
│   │   │   ├── fuel.py                  # Tasks: calculate_fuel_efficiency
│   │   │   ├── ai.py                    # Tasks: compute_insights, train_models
│   │   │   ├── reconciliation.py        # Tasks: reconcile_payments, validate_ledgers
│   │   │   └── audit.py                 # Tasks: archive_audit_logs, export_compliance
│   │   │
│   │   ├── notifications/               # Notification delivery
│   │   │   ├── __init__.py
│   │   │   ├── email.py                 # Email sender (SMTP, SendGrid, AWS SES)
│   │   │   ├── sms.py                   # SMS sender (Twilio, AWS SNS)
│   │   │   ├── webhook.py               # Webhook caller with retries
│   │   │   ├── templates.py             # Template rendering engine
│   │   │   └── providers.py             # Provider factory (multi-provider support)
│   │   │
│   │   ├── integrations/                # External service integrations
│   │   │   ├── __init__.py
│   │   │   ├── payment_gateway/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── razorpay.py          # Razorpay integration
│   │   │   │   ├── stripe.py            # Stripe integration
│   │   │   │   └── base.py              # Base gateway interface
│   │   │   ├── gps/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── google_maps.py       # Google Maps API
│   │   │   │   └── osm.py               # OpenStreetMap
│   │   │   ├── sms/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── twilio.py
│   │   │   │   └── aws_sns.py
│   │   │   ├── storage/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── s3.py                # AWS S3 file storage
│   │   │   │   └── local.py             # Local filesystem (dev)
│   │   │   └── messaging/
│   │   │       ├── __init__.py
│   │   │       ├── kafka.py             # Kafka event producer
│   │   │       └── rabbitmq.py          # RabbitMQ (alternative)
│   │   │
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── validators.py             # Custom validators (phone, GST, PAN)
│   │   │   ├── formatters.py             # Data formatters (currency, date, phone)
│   │   │   ├── parsers.py                # Data parsers (CSV import)
│   │   │   ├── calculations.py           # Math utilities (profit, tax, fuel efficiency)
│   │   │   ├── pagination.py             # Pagination helpers (cursor, offset)
│   │   │   ├── authorization.py          # Authorization helper functions
│   │   │   ├── cache.py                  # Redis cache wrapper
│   │   │   └── datetime.py               # Timezone-aware datetime utilities
│   │   │
│   │   ├── events/                       # Domain event definitions
│   │   │   ├── __init__.py
│   │   │   ├── base.py                   # Base event class
│   │   │   ├── booking.py                # BookingCreated, BookingCancelled, etc.
│   │   │   ├── trip.py                   # TripStarted, TripCompleted, etc.
│   │   │   ├── invoice.py                # InvoiceGenerated, InvoiePaid, etc.
│   │   │   ├── vehicle.py                # VehicleRegistrationExpiring, etc.
│   │   │   └── payment.py                # PaymentReceived, PaymentFailed, etc.
│   │   │
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── conftest.py               # pytest fixtures, test DB setup
│   │       ├── test_auth.py              # Auth and RBAC tests
│   │       ├── test_models.py            # Model validation and constraints
│   │       ├── test_repositories.py      # Repository CRUD tests
│   │       ├── test_services.py          # Service business logic tests
│   │       ├── test_api_customers.py     # Customer API endpoint tests
│   │       ├── test_api_bookings.py      # Booking API tests
│   │       ├── test_api_invoices.py      # Invoice API tests
│   │       ├── test_api_payments.py      # Payment API tests
│   │       ├── test_integration.py       # End-to-end workflow tests
│   │       ├── test_multi_tenant.py      # Multi-tenant isolation tests
│   │       ├── factories.py              # SQLAlchemy factories for test data
│   │       └── fixtures.py               # Shared fixtures
│   │
│   ├── alembic/                          # Database migrations
│   │   ├── versions/                     # Migration scripts
│   │   │   ├── 001_initial_schema.py
│   │   │   ├── 002_add_audit_triggers.py
│   │   │   └── ...
│   │   ├── env.py                        # Alembic environment config
│   │   └── script.py.mako                # Migration template
│   │
│   ├── docs/
│   │   ├── PHASE_1_ARCHITECTURE_REVIEW.md
│   │   ├── PHASE_2_FINAL_DATABASE_DESIGN.md
│   │   ├── PHASE_3_PROJECT_STRUCTURE.md
│   │   ├── api/
│   │   │   ├── customers.md              # Customer API documentation
│   │   │   ├── bookings.md
│   │   │   └── ...
│   │   ├── database/
│   │   │   ├── database_overview.md
│   │   │   ├── tables_reference.md
│   │   │   └── business_flows.md
│   │   ├── deployment/
│   │   │   ├── docker.md
│   │   │   ├── kubernetes.md
│   │   │   └── monitoring.md
│   │   ├── architecture/
│   │   │   ├── layers.md
│   │   │   ├── security.md
│   │   │   └── scalability.md
│   │   └── troubleshooting.md
│   │
│   ├── .env.example                      # Environment variables template
│   ├── .env.production                   # Production config (encrypted)
│   ├── .gitignore
│   ├── requirements.txt                  # Python dependencies
│   ├── requirements-dev.txt              # Development dependencies
│   ├── Dockerfile                        # Docker image build
│   ├── docker-compose.yml                # Local dev environment
│   ├── pytest.ini                        # Pytest configuration
│   ├── pyproject.toml                    # Python project metadata
│   ├── README.md
│   └── Makefile                          # Development commands
│
├── frontend/                              # React/Next.js (future)
└── infrastructure/
    ├── terraform/                         # IaC for AWS/cloud
    ├── helm/                              # Kubernetes helm charts
    ├── docker/
    │   ├── app.Dockerfile
    │   ├── worker.Dockerfile
    │   └── nginx.Dockerfile
    └── monitoring/                        # Prometheus, Grafana configs

```

---

## LAYER ARCHITECTURE DIAGRAM

```
┌─────────────────────────────────────────────────────────────┐
│                      API CLIENTS                             │
│  (Mobile, Web, Third-party integrations)                     │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        │                                     │
┌───────▼──────────┐              ┌──────────▼────────┐
│  API Router      │              │  WebSocket        │
│  (Endpoints)     │              │  (Real-time)      │
└───────┬──────────┘              └──────────┬────────┘
        │                                    │
        │  ┌────────────────────────────────┘
        │  │
┌───────▼──────────────────────────────────┐
│       MIDDLEWARE LAYER                   │
│  • Auth (JWT verification)               │
│  • Tenant isolation (X-Org-Id)           │
│  • Request ID tracking                   │
│  • Rate limiting                         │
│  • Error handling                        │
└───────┬──────────────────────────────────┘
        │
┌───────▼──────────────────────────────────┐
│       ROUTERS (api/v1/routers/)          │
│  • Validation (Pydantic)                 │
│  • Request/response mapping              │
│  • Call services                         │
└───────┬──────────────────────────────────┘
        │
┌───────▼──────────────────────────────────┐
│       SERVICES (services/)               │
│  • Business logic                        │
│  • Orchestration                         │
│  • Validation beyond schema              │
│  • Event publishing                      │
│  • External integrations                 │
└───────┬──────────────────────────────────┘
        │
    ┌───┴───┬────────────────┬──────────────┐
    │       │                │              │
┌───▼──┐  ┌─▼──────────┐  ┌──▼────────┐  ┌─▼──────────┐
│ REPO │  │ CACHE      │  │ EVENTS    │  │INTEGRATIONS│
│      │  │ (Redis)    │  │(Kafka)    │  │            │
└───┬──┘  └─┬──────────┘  └──┬────────┘  └─┬──────────┘
    │       │                │              │
    │       ├────────────────┤              │
    │       │                │              │
┌───▼───────▼────────────────▼──────────────▼──────┐
│            DATABASE Layer (PostgreSQL)           │
│  • Models (SQLAlchemy 2.0)                       │
│  • Session management                           │
│  • Connection pooling (pgbouncer)                │
│  • Row-Level Security (RLS)                      │
│  • Audit triggers                                │
└────────────────────────────────────────────────┘
            │
            ├─ Read Replicas (analytics queries)
            ├─ Debezium (CDC to Kafka)
            └─ Backups (WAL archiving, PITR)

┌────────────────────────────────────────────────┐
│      BACKGROUND WORKERS (Celery/Temporal)      │
│  • Async notifications                         │
│  • Invoice generation                          │
│  • Report aggregation                          │
│  • Maintenance scheduling                      │
│  • Reconciliation jobs                         │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│      ANALYTICS LAYER (ClickHouse/Data DW)      │
│  • CDC from Postgres via Kafka                 │
│  • Monthly aggregates                          │
│  • Trend analysis                              │
│  • ML feature store                            │
└────────────────────────────────────────────────┘
```

---

## LAYER DESCRIPTIONS

### 1. API Router Layer (api/v1/routers/)
**Purpose:** HTTP request handling, validation, authorization  
**Responsibility:**
- Parse and validate requests using Pydantic schemas
- Call service layer with business context
- Check authorization (RBAC permissions)
- Format and return responses
- Handle HTTP status codes (200, 201, 400, 404, 409, 500)

**Example Pattern:**
```python
@router.post("/customers", response_model=CustomerResponse, status_code=201)
def create_customer(
    req: CustomerCreate,
    current_user: User = Depends(get_current_user),
    org_id: UUID = Depends(get_current_org),
    db: Session = Depends(get_db),
):
    # Validate permission
    check_permission(current_user, "customers:create")
    # Call service
    customer = customer_service.create(db, org_id, req)
    return customer
```

### 2. Service Layer (services/)
**Purpose:** Business logic, orchestration, validation  
**Responsibility:**
- Implement business rules and workflows
- Call repositories for data access
- Validate beyond schema (duplicate checks, balance checks)
- Manage transactions and rollbacks
- Publish domain events
- Call external integrations
- Logging and error handling

**Example Pattern:**
```python
class CustomerService:
    def create(self, db: Session, org_id: UUID, req: CustomerCreate) -> Customer:
        # Validation
        self.validate_duplicate_phone(db, org_id, req.phone_number)
        self.validate_duplicate_gst(db, org_id, req.gst_number)
        
        # Business logic
        customer = self.repository.create(db, org_id, req)
        
        # Publish event
        event = CustomerCreatedEvent(customer_id=customer.id, org_id=org_id)
        self.event_service.publish(event)
        
        # Audit
        self.audit_service.log("customer", customer.id, "created")
        
        return customer
```

### 3. Repository Layer (repositories/)
**Purpose:** Data access abstraction  
**Responsibility:**
- Encapsulate all DB queries
- Implement CRUD operations
- Apply tenant filtering (organization_id)
- Return model instances or lists
- Handle pagination and sorting

**Example Pattern:**
```python
class CustomerRepository(BaseRepository):
    model = Customer
    
    def list_by_org(self, db: Session, org_id: UUID, skip=0, limit=50):
        return db.query(self.model)\
            .filter(self.model.organization_id == org_id)\
            .filter(self.model.deleted_at.is_(None))\
            .offset(skip).limit(limit).all()
    
    def get_by_phone(self, db: Session, org_id: UUID, phone: str):
        return db.query(self.model)\
            .filter(self.model.organization_id == org_id)\
            .filter(self.model.phone_number == phone)\
            .first()
```

### 4. Model Layer (db/models/)
**Purpose:** ORM mapping and data validation  
**Responsibility:**
- Define SQLAlchemy models with proper types
- Define relationships between tables
- Add constraints (UNIQUE, CHECK, FK)
- Define indexes and partitioning
- Use mixins (TimestampMixin, TenantMixin, SoftDeleteMixin)

### 5. Schema Layer (schemas/)
**Purpose:** Request/response validation and serialization  
**Responsibility:**
- Define Pydantic models for API I/O
- Validate input data (phone, email, GST formats)
- Transform ORM models to JSON responses
- Support versioning and evolution

**Example Pattern:**
```python
class CustomerCreate(BaseModel):
    customer_name: str
    phone_number: str
    email: Optional[EmailStr] = None
    gst_number: Optional[str] = None
    
    @field_validator('phone_number')
    def validate_phone(cls, v):
        if not re.match(r'^\+?\d{7,15}$', v):
            raise ValueError('Invalid phone format')
        return v

class CustomerResponse(BaseModel):
    id: int
    organization_id: UUID
    customer_name: str
    phone_number: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
```

### 6. Middleware Layer (middleware/)
**Purpose:** Cross-cutting concerns  
**Responsibility:**
- JWT verification and user context loading
- Tenant isolation (X-Org-Id header or JWT claim)
- Request ID generation for tracing
- Rate limiting per tenant
- Logging request/response metadata
- Error handling and exception translation

### 7. Background Workers (tasks/)
**Purpose:** Async job processing  
**Responsibility:**
- Email/SMS sending
- Invoice generation
- Report generation
- Data reconciliation
- Maintenance scheduling
- Model training

**Example Pattern:**
```python
@celery_app.task(bind=True, max_retries=3)
def send_invoice_email(self, invoice_id: int, recipient_email: str):
    try:
        invoice = invoice_service.get_by_id(invoice_id)
        email_service.send_invoice(invoice, recipient_email)
    except Exception as exc:
        self.retry(exc=exc, countdown=60)
```

### 8. Integration Layer (integrations/)
**Purpose:** External service connectors  
**Responsibility:**
- Payment gateway APIs (Razorpay, Stripe)
- GPS/mapping services (Google Maps)
- SMS providers (Twilio, AWS SNS)
- File storage (S3, local)
- Messaging (Kafka, RabbitMQ)

### 9. Event Layer (events/)
**Purpose:** Domain event definitions  
**Responsibility:**
- Define event classes
- Serialize/deserialize events
- Event versioning
- Publish to Kafka for CDC and downstream systems

---

## DEPENDENCY INJECTION PATTERN

All layers use FastAPI's `Depends()` for dependency injection:

```python
# deps.py
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id = payload.get("sub")
    return db.query(User).filter(User.id == user_id).first()

def get_current_org(
    current_user: User = Depends(get_current_user)
) -> UUID:
    return current_user.organization_id

def check_permission(
    required_permission: str,
    current_user: User = Depends(get_current_user)
):
    user_perms = get_user_permissions(current_user)
    if required_permission not in user_perms:
        raise HTTPException(403, "Insufficient permissions")
```

Then inject in routers:

```python
@router.post("/customers")
def create_customer(
    req: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    org_id: UUID = Depends(get_current_org),
):
    check_permission("customers:create", current_user)
    return customer_service.create(db, org_id, req)
```

---

## CONFIGURATION MANAGEMENT (core/config.py)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App
    APP_NAME: str = "VahanOne"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 40
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    JWT_REFRESH_EXPIRATION_DAYS: int = 7
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC_PREFIX: str = "vahanone."
    
    # AWS
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    
    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    
    # Logging
    LOG_LEVEL: str = "INFO"
    SENTRY_DSN: Optional[str] = None
    
    # SMTP
    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

---

## DATABASE SESSION MANAGEMENT (db/session.py)

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,  # Verify connections before using
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## MAIN APP INITIALIZATION (main.py)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.config import settings
from core.logging import setup_logging
from middleware import (
    tenant_middleware,
    auth_middleware,
    error_handler_middleware,
    request_id_middleware,
    rate_limit_middleware,
)
from api.v1 import router as v1_router

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting VahanOne API")
    # Migrations could run here
    yield
    # Shutdown
    logger.info("Shutting down VahanOne API")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware (order matters)
app.add_middleware(error_handler_middleware)
app.add_middleware(request_id_middleware)
app.add_middleware(rate_limit_middleware)
app.add_middleware(tenant_middleware)
app.add_middleware(auth_middleware)

# Routes
app.include_router(v1_router, prefix="/api/v1")

# Health checks
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/readiness")
def readiness():
    return {"status": "ready"}
```

---

## API VERSIONING STRATEGY

- All endpoints prefixed with `/api/v1/`
- Use API versioning for backward compatibility
- Deploy v2 alongside v1; gradually sunset v1
- Support multiple versions in prod for 6-12 months during transition

---

## TESTING STRUCTURE (tests/)

Each module has corresponding test file:
- `services/customer.py` → `tests/test_services_customer.py`
- `repositories/vehicle.py` → `tests/test_repositories_vehicle.py`
- `api/v1/routers/bookings.py` → `tests/test_api_bookings.py`

Test pyramid:
- **Unit Tests** (70%): Services, repositories, utils
- **Integration Tests** (20%): DB transactions, workflows
- **API Tests** (10%): Full request/response cycles

---

## RECOMMENDED DEPLOYMENT ARCHITECTURE

```
┌──────────────────────────────────────────────────────────┐
│                    AWS/GCP/EKS                           │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Load Balancer (ALB/NLB)                           │  │
│  └────────────┬───────────────────────────────────────┘  │
│               │                                           │
│    ┌──────────┼──────────┐                               │
│    ▼          ▼          ▼                               │
│  ┌────────┐ ┌────────┐ ┌────────┐                        │
│  │ FastAPI│ │FastAPI │ │FastAPI │  (3-5 replicas)      │
│  │ Pod 1  │ │ Pod 2  │ │ Pod 3  │  (Horizontal scale)   │
│  └────────┘ └────────┘ └────────┘                        │
│                                                          │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  Postgres (RDS Primary + Read Replicas)             │ │
│  │  pgbouncer (connection pooling)                      │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  Redis (Caching, rate limiting, sessions)           │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  Kafka (Event streaming, CDC)                        │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌────────┐ ┌────────┐ ┌────────┐  (Celery workers)    │
│  │Worker 1│ │Worker 2│ │Worker 3│  (Auto-scale on load)│
│  └────────┘ └────────┘ └────────┘                        │
│                                                          │
└──────────────────────────────────────────────────────────┘

External:
  • S3 (Document storage)
  • CloudWatch/DataDog (Monitoring)
  • Sentry (Error tracking)
  • ClickHouse (Analytics)
```

---

**END OF PHASE 3: Project Structure Blueprint**

This structure provides:
✓ Clean separation of concerns  
✓ Scalable to 100k+ organizations  
✓ Easy testing and mocking  
✓ Clear dependency flow  
✓ Extensible for new features  
✓ Production-ready deployment patterns  

**Shall I proceed with PHASE 4: Security Implementation (JWT, RBAC, RLS)?**
