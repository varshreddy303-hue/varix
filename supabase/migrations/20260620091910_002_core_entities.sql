CREATE TABLE customers (
    id BIGSERIAL PRIMARY KEY,
    customer_name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(32) NOT NULL,
    email VARCHAR(255),
    gst_number VARCHAR(32),
    address VARCHAR(500),
    city VARCHAR(100),
    state VARCHAR(100),
    pincode VARCHAR(12),
    notes TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    company VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    organization_id UUID NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE,
    UNIQUE (organization_id, gst_number),
    UNIQUE (organization_id, phone_number)
);

ALTER TABLE customers ENABLE ROW LEVEL SECURITY;

CREATE INDEX ix_customers_organization_id ON customers (organization_id);
CREATE INDEX ix_customers_org_phone ON customers (organization_id, phone_number);
CREATE INDEX ix_customers_org_gst ON customers (organization_id, gst_number);

CREATE TABLE drivers (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    license_number VARCHAR(64) NOT NULL,
    license_expiry TIMESTAMP WITH TIME ZONE,
    contact_number VARCHAR(32),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    organization_id UUID NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE,
    UNIQUE (organization_id, license_number)
);

ALTER TABLE drivers ENABLE ROW LEVEL SECURITY;

CREATE INDEX ix_drivers_organization_id ON drivers (organization_id);

CREATE TABLE vehicles (
    id BIGSERIAL PRIMARY KEY,
    vehicle_number VARCHAR(64) NOT NULL,
    vehicle_type VARCHAR(64),
    make VARCHAR(128),
    model VARCHAR(128),
    seating_capacity INTEGER,
    fuel_type VARCHAR(64),
    registration_date TIMESTAMP WITH TIME ZONE,
    insurance_expiry_date TIMESTAMP WITH TIME ZONE,
    permit_expiry_date TIMESTAMP WITH TIME ZONE,
    fc_expiry_date TIMESTAMP WITH TIME ZONE,
    pollution_expiry_date TIMESTAMP WITH TIME ZONE,
    road_tax_expiry_date TIMESTAMP WITH TIME ZONE,
    purchase_price NUMERIC(12, 2),
    emi_amount NUMERIC(12, 2),
    emi_due_day INTEGER,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    gps_subscription_expiry_date TIMESTAMP WITH TIME ZONE,
    service_due_date TIMESTAMP WITH TIME ZONE,
    tyre_change_due_date TIMESTAMP WITH TIME ZONE,
    battery_change_due_date TIMESTAMP WITH TIME ZONE,
    loan_closure_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    organization_id UUID NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE,
    UNIQUE (organization_id, vehicle_number)
);

ALTER TABLE vehicles ENABLE ROW LEVEL SECURITY;

CREATE INDEX ix_vehicles_organization_id ON vehicles (organization_id);
CREATE INDEX ix_vehicles_org_number ON vehicles (organization_id, vehicle_number);

CREATE TABLE trip_packages (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    package_category VARCHAR(64) NOT NULL,
    included_hours INTEGER,
    included_km INTEGER,
    base_amount NUMERIC(12, 2) NOT NULL DEFAULT 0,
    extra_km_rate NUMERIC(12, 2),
    extra_hour_rate NUMERIC(12, 2),
    driver_bata_default NUMERIC(12, 2),
    night_charge_default NUMERIC(12, 2),
    permit_default NUMERIC(12, 2),
    state_tax_default NUMERIC(12, 2),
    minimum_km_per_day INTEGER,
    km_rate NUMERIC(12, 2),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    organization_id UUID NOT NULL,
    UNIQUE (organization_id, name)
);

ALTER TABLE trip_packages ENABLE ROW LEVEL SECURITY;

CREATE INDEX ix_trip_packages_organization_id ON trip_packages (organization_id);
CREATE INDEX ix_trip_packages_org_category ON trip_packages (organization_id, package_category);