"""Add advance_received fields and customer company

Revision ID: e5d4c3b2a1f0
Revises: 1a2b3c4d5e6f
Create Date: 2026-06-08 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = 'e5d4c3b2a1f0'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'customers',
        sa.Column('company', sa.String(length=255), nullable=True),
    )
    op.add_column(
        'trips',
        sa.Column('advance_received', sa.Numeric(12, 2), nullable=True, server_default='0'),
    )
    op.add_column(
        'invoices',
        sa.Column('advance_received', sa.Numeric(12, 2), nullable=True, server_default='0'),
    )


def downgrade() -> None:
    op.drop_column('invoices', 'advance_received')
    op.drop_column('trips', 'advance_received')
    op.drop_column('customers', 'company')
