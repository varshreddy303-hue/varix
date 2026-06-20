CREATE TABLE invoices (
    id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT REFERENCES customers(id) ON DELETE RESTRICT,
    trip_id BIGINT REFERENCES trips(id) ON DELETE CASCADE,
    booking_id BIGINT REFERENCES bookings(id) ON DELETE SET NULL,
    due_date TIMESTAMP WITH TIME ZONE,
    status VARCHAR(32) NOT NULL DEFAULT 'draft',
    notes TEXT,
    metadata JSONB,
    invoice_number VARCHAR(128),
    invoice_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    subtotal NUMERIC(12, 2) NOT NULL DEFAULT 0,
    tax_amount NUMERIC(12, 2) NOT NULL DEFAULT 0,
    total_amount NUMERIC(12, 2) NOT NULL DEFAULT 0,
    advance_received NUMERIC(12, 2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    organization_id UUID NOT NULL,
    UNIQUE (organization_id, invoice_number),
    UNIQUE (trip_id)
);

ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;

CREATE INDEX ix_invoices_customer_id ON invoices (customer_id);
CREATE INDEX ix_invoices_organization_id ON invoices (organization_id);
CREATE INDEX ix_invoices_org_customer ON invoices (organization_id, customer_id);
CREATE INDEX ix_invoices_org_trip ON invoices (organization_id, trip_id);
CREATE INDEX ix_invoices_org_booking ON invoices (organization_id, booking_id);

CREATE TABLE invoice_items (
    id BIGSERIAL PRIMARY KEY,
    invoice_id BIGINT NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    description VARCHAR(512),
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price_cents BIGINT NOT NULL,
    line_total_cents BIGINT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    organization_id UUID NOT NULL
);

ALTER TABLE invoice_items ENABLE ROW LEVEL SECURITY;

CREATE INDEX ix_invoice_items_invoice_id ON invoice_items (invoice_id);
CREATE INDEX ix_invoice_items_organization_id ON invoice_items (organization_id);
CREATE INDEX ix_invoice_items_org_invoice ON invoice_items (organization_id, invoice_id);

CREATE TABLE payments (
    id BIGSERIAL PRIMARY KEY,
    invoice_id BIGINT NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    amount_cents BIGINT NOT NULL,
    method VARCHAR(64),
    transaction_ref VARCHAR(255),
    status VARCHAR(64),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    organization_id UUID NOT NULL
);

ALTER TABLE payments ENABLE ROW LEVEL SECURITY;

CREATE INDEX ix_payments_invoice_id ON payments (invoice_id);
CREATE INDEX ix_payments_organization_id ON payments (organization_id);
CREATE INDEX ix_payments_org_invoice ON payments (organization_id, invoice_id);

CREATE TABLE expenses (
    id BIGSERIAL PRIMARY KEY,
    trip_id BIGINT REFERENCES trips(id) ON DELETE CASCADE,
    vehicle_id BIGINT NOT NULL REFERENCES vehicles(id) ON DELETE RESTRICT,
    booking_id BIGINT REFERENCES bookings(id) ON DELETE SET NULL,
    category VARCHAR(32) NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    description TEXT,
    expense_date TIMESTAMP WITH TIME ZONE NOT NULL,
    fuel_amount NUMERIC(12, 2) DEFAULT 0,
    toll_amount NUMERIC(12, 2) DEFAULT 0,
    parking_amount NUMERIC(12, 2) DEFAULT 0,
    driver_bata_amount NUMERIC(12, 2) DEFAULT 0,
    permit_amount NUMERIC(12, 2) DEFAULT 0,
    state_tax_amount NUMERIC(12, 2) DEFAULT 0,
    food_amount NUMERIC(12, 2) DEFAULT 0,
    accommodation_amount NUMERIC(12, 2) DEFAULT 0,
    misc_amount NUMERIC(12, 2) DEFAULT 0,
    total_amount NUMERIC(12, 2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    organization_id UUID NOT NULL
);

ALTER TABLE expenses ENABLE ROW LEVEL SECURITY;

CREATE INDEX ix_expenses_organization_id ON expenses (organization_id);
CREATE INDEX ix_expenses_trip_id ON expenses (trip_id);
CREATE INDEX ix_expenses_vehicle_id ON expenses (vehicle_id);
CREATE INDEX ix_expenses_booking_id ON expenses (booking_id);
CREATE INDEX ix_expenses_category ON expenses (category);
CREATE INDEX ix_expenses_expense_date ON expenses (expense_date);
CREATE INDEX ix_expenses_org_trip ON expenses (organization_id, trip_id);
CREATE INDEX ix_expenses_org_vehicle ON expenses (organization_id, vehicle_id);
CREATE INDEX ix_expenses_org_booking ON expenses (organization_id, booking_id);