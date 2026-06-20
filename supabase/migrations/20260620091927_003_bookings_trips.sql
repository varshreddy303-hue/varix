CREATE TABLE bookings (
    id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT REFERENCES customers(id) ON DELETE RESTRICT,
    vehicle_id BIGINT NOT NULL REFERENCES vehicles(id) ON DELETE RESTRICT,
    driver_id BIGINT REFERENCES drivers(id) ON DELETE SET NULL,
    pickup_location VARCHAR(500) NOT NULL,
    destination VARCHAR(500) NOT NULL,
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    end_date TIMESTAMP WITH TIME ZONE NOT NULL,
    booking_amount NUMERIC(12, 2) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'pending',
    customer_name VARCHAR(255),
    customer_company VARCHAR(255),
    customer_phone VARCHAR(32),
    customer_email VARCHAR(255),
    customer_gst_number VARCHAR(32),
    customer_city VARCHAR(100),
    customer_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    organization_id UUID NOT NULL
);

ALTER TABLE bookings ENABLE ROW LEVEL SECURITY;

CREATE INDEX ix_bookings_customer_id ON bookings (customer_id);
CREATE INDEX ix_bookings_driver_id ON bookings (driver_id);
CREATE INDEX ix_bookings_vehicle_id ON bookings (vehicle_id);
CREATE INDEX ix_bookings_organization_id ON bookings (organization_id);
CREATE INDEX ix_bookings_start_date ON bookings (start_date);
CREATE INDEX ix_bookings_end_date ON bookings (end_date);
CREATE INDEX ix_bookings_org_customer ON bookings (organization_id, customer_id);
CREATE INDEX ix_bookings_org_vehicle ON bookings (organization_id, vehicle_id);
CREATE INDEX ix_bookings_org_start_date ON bookings (organization_id, start_date);

CREATE TABLE trips (
    id BIGSERIAL PRIMARY KEY,
    booking_id BIGINT NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    vehicle_id BIGINT NOT NULL REFERENCES vehicles(id) ON DELETE RESTRICT,
    package_id BIGINT REFERENCES trip_packages(id) ON DELETE SET NULL,
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    distance_km NUMERIC(12, 3),
    start_km BIGINT,
    end_km BIGINT,
    trip_revenue NUMERIC(12, 2),
    status VARCHAR(32) NOT NULL DEFAULT 'pending',
    notes TEXT,
    advance_received NUMERIC(12, 2) DEFAULT 0,
    extra_km_rate NUMERIC(12, 2),
    extra_hour_rate NUMERIC(12, 2),
    minimum_km_per_day INTEGER,
    km_rate NUMERIC(12, 2),
    package_name VARCHAR(255),
    trip_date DATE,
    start_place VARCHAR(500),
    end_place VARCHAR(500),
    included_km INTEGER,
    included_hours INTEGER,
    hours_used NUMERIC(8, 2),
    days_used INTEGER,
    extra_km NUMERIC(12, 3),
    extra_hours NUMERIC(8, 2),
    package_amount NUMERIC(12, 2),
    extra_km_amount NUMERIC(12, 2),
    extra_hour_amount NUMERIC(12, 2),
    driver_bata NUMERIC(12, 2),
    night_charges NUMERIC(12, 2),
    permit_amount NUMERIC(12, 2),
    state_tax_amount NUMERIC(12, 2),
    toll_amount NUMERIC(12, 2),
    parking_amount NUMERIC(12, 2),
    grand_total NUMERIC(12, 2),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    organization_id UUID NOT NULL
);

ALTER TABLE trips ENABLE ROW LEVEL SECURITY;

CREATE INDEX ix_trips_organization_id ON trips (organization_id);
CREATE INDEX ix_trips_start_time ON trips (start_time);
CREATE INDEX ix_trips_end_time ON trips (end_time);
CREATE INDEX ix_trips_status ON trips (status);
CREATE INDEX ix_trips_booking_id ON trips (booking_id);
CREATE INDEX ix_trips_vehicle_id ON trips (vehicle_id);
CREATE INDEX ix_trips_package_id ON trips (package_id);
CREATE INDEX ix_trips_org_start ON trips (organization_id, start_time);
CREATE INDEX ix_trips_org_booking ON trips (organization_id, booking_id);
CREATE INDEX ix_trips_org_vehicle ON trips (organization_id, vehicle_id);