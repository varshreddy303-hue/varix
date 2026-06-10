"""add_reminder_engine

Revision ID: f2f3e4d5c6b7
Revises: b7c1e3a5d2f4
Create Date: 2026-06-08 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'f2f3e4d5c6b7'
down_revision = 'b7c1e3a5d2f4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('vehicles', sa.Column('gps_subscription_expiry_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('vehicles', sa.Column('service_due_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('vehicles', sa.Column('tyre_change_due_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('vehicles', sa.Column('battery_change_due_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('vehicles', sa.Column('loan_closure_date', sa.DateTime(timezone=True), nullable=True))

    op.create_table(
        'reminder_rules',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=64), nullable=False),
        sa.Column('event_type', sa.String(length=128), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('trigger_days_before', sa.Integer(), nullable=True),
        sa.Column('threshold_hours', sa.Integer(), nullable=True),
        sa.Column('priority', sa.Integer(), server_default='100', nullable=False),
        sa.Column('settings', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
    )
    op.create_index(op.f('ix_reminder_rules_org_event_type'), 'reminder_rules', ['organization_id', 'event_type'], unique=False)

    op.create_table(
        'reminders',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('rule_id', sa.BigInteger(), sa.ForeignKey('reminder_rules.id', ondelete='CASCADE'), nullable=False),
        sa.Column('entity_type', sa.String(length=100), nullable=True),
        sa.Column('entity_id', sa.BigInteger(), nullable=True),
        sa.Column('reminder_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='pending'),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('payload', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
    )
    op.create_index(op.f('ix_reminders_org_status'), 'reminders', ['organization_id', 'status'], unique=False)
    op.create_index(op.f('ix_reminders_org_reminder_date'), 'reminders', ['organization_id', 'reminder_date'], unique=False)

    op.create_table(
        'notification_events',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('reminder_id', sa.BigInteger(), sa.ForeignKey('reminders.id', ondelete='CASCADE'), nullable=True),
        sa.Column('event_type', sa.String(length=128), nullable=False),
        sa.Column('recipient_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('channel', sa.String(length=32), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='pending'),
        sa.Column('scheduled_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('payload', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
    )
    op.create_index(op.f('ix_notification_events_org_scheduled'), 'notification_events', ['organization_id', 'scheduled_time'], unique=False)

    op.create_table(
        'notification_preferences',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('event_type', sa.String(length=128), nullable=False),
        sa.Column('channel', sa.String(length=32), nullable=False),
        sa.Column('enabled', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
    )
    op.create_index(op.f('ix_notification_preferences_org_event_channel'), 'notification_preferences', ['organization_id', 'event_type', 'channel'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_notification_preferences_org_event_channel'), table_name='notification_preferences')
    op.drop_table('notification_preferences')

    op.drop_index(op.f('ix_notification_events_org_scheduled'), table_name='notification_events')
    op.drop_table('notification_events')

    op.drop_index(op.f('ix_reminders_org_reminder_date'), table_name='reminders')
    op.drop_index(op.f('ix_reminders_org_status'), table_name='reminders')
    op.drop_table('reminders')

    op.drop_index(op.f('ix_reminder_rules_org_event_type'), table_name='reminder_rules')
    op.drop_table('reminder_rules')

    op.drop_column('vehicles', 'loan_closure_date')
    op.drop_column('vehicles', 'battery_change_due_date')
    op.drop_column('vehicles', 'tyre_change_due_date')
    op.drop_column('vehicles', 'service_due_date')
    op.drop_column('vehicles', 'gps_subscription_expiry_date')
