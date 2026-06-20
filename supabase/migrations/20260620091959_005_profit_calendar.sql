CREATE TABLE trip_profit_summary (
    id BIGSERIAL PRIMARY KEY,
    trip_id BIGINT NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    vehicle_id BIGINT NOT NULL REFERENCES vehicles(id) ON DELETE RESTRICT,
    trip_revenue NUMERIC(12, 2) NOT NULL,
    total_expense NUMERIC(12, 2) NOT NULL,
    trip_profit NUMERIC(12, 2) NOT NULL,
    profit_date DATE NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    organization_id UUID NOT NULL,
    UNIQUE (trip_id)
);

ALTER TABLE trip_profit_summary ENABLE ROW LEVEL SECURITY;

CREATE INDEX ix_trip_profit_summary_org_trip ON trip_profit_summary (organization_id, trip_id);
CREATE INDEX ix_trip_profit_summary_org_vehicle ON trip_profit_summary (organization_id, vehicle_id);
CREATE INDEX ix_trip_profit_summary_profit_date ON trip_profit_summary (profit_date);
CREATE INDEX ix_trip_profit_summary_year_month ON trip_profit_summary (year, month);

CREATE TABLE vehicle_daily_profit (
    id BIGSERIAL PRIMARY KEY,
    vehicle_id BIGINT NOT NULL REFERENCES vehicles(id) ON DELETE RESTRICT,
    profit_date DATE NOT NULL,
    total_revenue NUMERIC(12, 2) NOT NULL,
    total_expense NUMERIC(12, 2) NOT NULL,
    total_profit NUMERIC(12, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    organization_id UUID NOT NULL,
    UNIQUE (vehicle_id, profit_date)
);

ALTER TABLE vehicle_daily_profit ENABLE ROW LEVEL SECURITY;

CREATE INDEX ix_vehicle_daily_profit_org_vehicle ON vehicle_daily_profit (organization_id, vehicle_id);
CREATE INDEX ix_vehicle_daily_profit_profit_date ON vehicle_daily_profit (profit_date);

CREATE TABLE vehicle_monthly_profit (
    id BIGSERIAL PRIMARY KEY,
    vehicle_id BIGINT NOT NULL REFERENCES vehicles(id) ON DELETE RESTRICT,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    total_revenue NUMERIC(12, 2) NOT NULL,
    total_expense NUMERIC(12, 2) NOT NULL,
    total_profit NUMERIC(12, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    organization_id UUID NOT NULL,
    UNIQUE (vehicle_id, year, month)
);

ALTER TABLE vehicle_monthly_profit ENABLE ROW LEVEL SECURITY;

CREATE INDEX ix_vehicle_monthly_profit_org_vehicle ON vehicle_monthly_profit (organization_id, vehicle_id);
CREATE INDEX ix_vehicle_monthly_profit_year_month ON vehicle_monthly_profit (year, month);

CREATE TABLE maintenance_schedule (
    id BIGSERIAL PRIMARY KEY,
    organization_id UUID NOT NULL,
    vehicle_id BIGINT NOT NULL REFERENCES vehicles(id) ON DELETE RESTRICT,
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    end_date TIMESTAMP WITH TIME ZONE NOT NULL,
    reason VARCHAR(500) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'scheduled',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

ALTER TABLE maintenance_schedule ENABLE ROW LEVEL SECURITY;

CREATE INDEX ix_maintenance_schedule_org_vehicle ON maintenance_schedule (organization_id, vehicle_id);
CREATE INDEX ix_maintenance_schedule_org_start_date ON maintenance_schedule (organization_id, start_date);

CREATE TABLE vehicle_calendar_events (
    id BIGSERIAL PRIMARY KEY,
    organization_id UUID NOT NULL,
    vehicle_id BIGINT NOT NULL REFERENCES vehicles(id) ON DELETE RESTRICT,
    booking_id BIGINT REFERENCES bookings(id) ON DELETE CASCADE,
    maintenance_id BIGINT REFERENCES maintenance_schedule(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    event_type VARCHAR(32) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'pending',
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    end_date TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

ALTER TABLE vehicle_calendar_events ENABLE ROW LEVEL SECURITY;

CREATE INDEX ix_vehicle_calendar_events_org_vehicle ON vehicle_calendar_events (organization_id, vehicle_id);
CREATE INDEX ix_vehicle_calendar_events_org_start_date ON vehicle_calendar_events (organization_id, start_date);