"""Add detailed expense components

Revision ID: e5d4c3b2a1f1
Revises: e5d4c3b2a1f0
Create Date: 2026-06-08 00:05:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = 'e5d4c3b2a1f1'
down_revision = 'e5d4c3b2a1f0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('expenses', sa.Column('fuel_amount', sa.Numeric(12, 2), nullable=True, server_default='0'))
    op.add_column('expenses', sa.Column('toll_amount', sa.Numeric(12, 2), nullable=True, server_default='0'))
    op.add_column('expenses', sa.Column('parking_amount', sa.Numeric(12, 2), nullable=True, server_default='0'))
    op.add_column('expenses', sa.Column('driver_bata_amount', sa.Numeric(12, 2), nullable=True, server_default='0'))
    op.add_column('expenses', sa.Column('permit_amount', sa.Numeric(12, 2), nullable=True, server_default='0'))
    op.add_column('expenses', sa.Column('state_tax_amount', sa.Numeric(12, 2), nullable=True, server_default='0'))
    op.add_column('expenses', sa.Column('food_amount', sa.Numeric(12, 2), nullable=True, server_default='0'))
    op.add_column('expenses', sa.Column('accommodation_amount', sa.Numeric(12, 2), nullable=True, server_default='0'))
    op.add_column('expenses', sa.Column('misc_amount', sa.Numeric(12, 2), nullable=True, server_default='0'))
    op.add_column('expenses', sa.Column('total_amount', sa.Numeric(12, 2), nullable=True, server_default='0'))


def downgrade() -> None:
    op.drop_column('expenses', 'total_amount')
    op.drop_column('expenses', 'misc_amount')
    op.drop_column('expenses', 'accommodation_amount')
    op.drop_column('expenses', 'food_amount')
    op.drop_column('expenses', 'state_tax_amount')
    op.drop_column('expenses', 'permit_amount')
    op.drop_column('expenses', 'driver_bata_amount')
    op.drop_column('expenses', 'parking_amount')
    op.drop_column('expenses', 'toll_amount')
    op.drop_column('expenses', 'fuel_amount')
