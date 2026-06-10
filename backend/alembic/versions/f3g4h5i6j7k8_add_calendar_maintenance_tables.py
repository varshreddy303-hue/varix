"""Add vehicle calendar events and maintenance schedule tables

Revision ID: f3g4h5i6j7k8
Revises: e5d4c3b2a1f0
Create Date: 2026-06-08 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'f3g4h5i6j7k8'
down_revision = 'e5d4c3b2a1f0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'maintenance_schedule',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('vehicle_id', sa.BigInteger(), nullable=False),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('reason', sa.String(length=500), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='scheduled'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_maintenance_schedule_org_vehicle', 'maintenance_schedule', ['organization_id', 'vehicle_id'])
    op.create_index('ix_maintenance_schedule_org_start_date', 'maintenance_schedule', ['organization_id', 'start_date'])

    calendar_event_type = postgresql.ENUM('booking', 'maintenance', 'dispatch', name='calendar_event_type', create_type=False)
    calendar_event_type.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'vehicle_calendar_events',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('vehicle_id', sa.BigInteger(), nullable=False),
        sa.Column('booking_id', sa.BigInteger(), nullable=True),
        sa.Column('maintenance_id', sa.BigInteger(), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('event_type', calendar_event_type, nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='pending'),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_vehicle_calendar_events_org_vehicle', 'vehicle_calendar_events', ['organization_id', 'vehicle_id'])
    op.create_index('ix_vehicle_calendar_events_org_start_date', 'vehicle_calendar_events', ['organization_id', 'start_date'])


def downgrade() -> None:
    op.drop_index('ix_vehicle_calendar_events_org_start_date', table_name='vehicle_calendar_events')
    op.drop_index('ix_vehicle_calendar_events_org_vehicle', table_name='vehicle_calendar_events')
    op.drop_table('vehicle_calendar_events')
    op.drop_index('ix_maintenance_schedule_org_start_date', table_name='maintenance_schedule')
    op.drop_index('ix_maintenance_schedule_org_vehicle', table_name='maintenance_schedule')
    op.drop_table('maintenance_schedule')
    postgresql.ENUM('booking', 'maintenance', 'dispatch', name='calendar_event_type').drop(op.get_bind(), checkfirst=True)
