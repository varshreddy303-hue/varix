"""Add booking support to invoices and allow booking-only invoices.

Revision ID: 6b7c8d9e0f1
Revises: 5a6b7c8d9e0f
Create Date: 2026-06-09 00:30:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = '6b7c8d9e0f1'
down_revision = '5a6b7c8d9e0f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('invoices', sa.Column('booking_id', sa.BigInteger(), sa.ForeignKey('bookings.id', ondelete='SET NULL'), nullable=True))
    op.alter_column('invoices', 'customer_id', existing_type=sa.BigInteger(), nullable=True)
    op.alter_column('invoices', 'trip_id', existing_type=sa.BigInteger(), nullable=True)
    op.create_index('ix_invoices_org_booking', 'invoices', ['organization_id', 'booking_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_invoices_org_booking', table_name='invoices')
    op.drop_column('invoices', 'booking_id')
    op.alter_column('invoices', 'trip_id', existing_type=sa.BigInteger(), nullable=False)
    op.alter_column('invoices', 'customer_id', existing_type=sa.BigInteger(), nullable=False)
