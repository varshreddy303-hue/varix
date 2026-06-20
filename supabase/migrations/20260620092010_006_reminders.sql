CREATE TABLE reminder_rules (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(64) NOT NULL,
    event_type VARCHAR(128) NOT NULL,
    description TEXT,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    trigger_days_before INTEGER,
    threshold_hours INTEGER,
    priority INTEGER NOT NULL DEFAULT 100,
    settings JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    organization_id UUID NOT NULL
);

ALTER TABLE reminder_rules ENABLE ROW LEVEL SECURITY;

CREATE INDEX ix_reminder_rules_org_event_type ON reminder_rules (organization_id, event_type);

CREATE TABLE reminders (
    id BIGSERIAL PRIMARY KEY,
    rule_id BIGINT NOT NULL REFERENCES reminder_rules(id) ON DELETE CASCADE,
    entity_type VARCHAR(100),
    entity_id BIGINT,
    reminder_date TIMESTAMP WITH TIME ZONE NOT NULL,
    due_date TIMESTAMP WITH TIME ZONE,
    status VARCHAR(32) NOT NULL DEFAULT 'pending',
    message TEXT,
    payload JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    organization_id UUID NOT NULL
);

ALTER TABLE reminders ENABLE ROW LEVEL SECURITY;

CREATE INDEX ix_reminders_org_status ON reminders (organization_id, status);
CREATE INDEX ix_reminders_org_reminder_date ON reminders (organization_id, reminder_date);

CREATE TABLE notification_events (
    id BIGSERIAL PRIMARY KEY,
    reminder_id BIGINT REFERENCES reminders(id) ON DELETE CASCADE,
    event_type VARCHAR(128) NOT NULL,
    recipient_id UUID,
    channel VARCHAR(32) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'pending',
    scheduled_time TIMESTAMP WITH TIME ZONE,
    payload JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    organization_id UUID NOT NULL
);

ALTER TABLE notification_events ENABLE ROW LEVEL SECURITY;

CREATE INDEX ix_notification_events_org_scheduled ON notification_events (organization_id, scheduled_time);

CREATE TABLE notification_preferences (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID,
    event_type VARCHAR(128) NOT NULL,
    channel VARCHAR(32) NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    organization_id UUID NOT NULL,
    UNIQUE (organization_id, user_id, event_type, channel)
);

ALTER TABLE notification_preferences ENABLE ROW LEVEL SECURITY;

CREATE INDEX ix_notification_preferences_org_event_channel ON notification_preferences (organization_id, event_type, channel);