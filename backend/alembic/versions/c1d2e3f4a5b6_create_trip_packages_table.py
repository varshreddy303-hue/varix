"""create_trip_packages_table

Revision ID: c1d2e3f4a5b6
Revises: 1a2b3c4d5e6f,9f4e8c27a1b3,f2f3e4d5c6b7
Create Date: 2026-06-08 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1d2e3f4a5b6'
down_revision = ('1a2b3c4d5e6f', '9f4e8c27a1b3', 'f2f3e4d5c6b7')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'trip_packages',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('package_category', sa.String(length=64), nullable=False),
        sa.Column('included_hours', sa.Integer(), nullable=True),
        sa.Column('included_km', sa.Integer(), nullable=True),
        sa.Column('base_amount', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'),
        sa.Column('extra_km_rate', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('extra_hour_rate', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('driver_bata_default', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('night_charge_default', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('permit_default', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('state_tax_default', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('minimum_km_per_day', sa.Integer(), nullable=True),
        sa.Column('km_rate', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'name', name='uq_trip_packages_org_name'),
    )
    op.create_index('ix_trip_packages_org_category', 'trip_packages', ['organization_id', 'package_category'], unique=False)
    op.create_index(op.f('ix_trip_packages_organization_id'), 'trip_packages', ['organization_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_trip_packages_organization_id'), table_name='trip_packages')
    op.drop_index('ix_trip_packages_org_category', table_name='trip_packages')
    op.drop_table('trip_packages')
