"""extend_trip_package_fields

Revision ID: d1e2f3g4h5i6
Revises: c1d2e3f4a5b6
Create Date: 2026-06-08 00:30:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1e2f3g4h5i6'
down_revision = 'c1d2e3f4a5b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('trips', sa.Column('package_id', sa.BigInteger(), nullable=True))
    op.add_column('trips', sa.Column('package_name', sa.String(length=255), nullable=True))
    op.add_column('trips', sa.Column('trip_date', sa.Date(), nullable=True))
    op.add_column('trips', sa.Column('start_place', sa.String(length=500), nullable=True))
    op.add_column('trips', sa.Column('end_place', sa.String(length=500), nullable=True))
    op.add_column('trips', sa.Column('included_km', sa.Integer(), nullable=True))
    op.add_column('trips', sa.Column('included_hours', sa.Integer(), nullable=True))
    op.add_column('trips', sa.Column('hours_used', sa.Numeric(precision=8, scale=2), nullable=True))
    op.add_column('trips', sa.Column('days_used', sa.Integer(), nullable=True))
    op.add_column('trips', sa.Column('extra_km', sa.Numeric(precision=12, scale=3), nullable=True))
    op.add_column('trips', sa.Column('extra_hours', sa.Numeric(precision=8, scale=2), nullable=True))
    op.add_column('trips', sa.Column('package_amount', sa.Numeric(precision=12, scale=2), nullable=True))
    op.add_column('trips', sa.Column('extra_km_amount', sa.Numeric(precision=12, scale=2), nullable=True))
    op.add_column('trips', sa.Column('extra_hour_amount', sa.Numeric(precision=12, scale=2), nullable=True))
    op.add_column('trips', sa.Column('driver_bata', sa.Numeric(precision=12, scale=2), nullable=True))
    op.add_column('trips', sa.Column('night_charges', sa.Numeric(precision=12, scale=2), nullable=True))
    op.add_column('trips', sa.Column('permit_amount', sa.Numeric(precision=12, scale=2), nullable=True))
    op.add_column('trips', sa.Column('state_tax_amount', sa.Numeric(precision=12, scale=2), nullable=True))
    op.add_column('trips', sa.Column('toll_amount', sa.Numeric(precision=12, scale=2), nullable=True))
    op.add_column('trips', sa.Column('parking_amount', sa.Numeric(precision=12, scale=2), nullable=True))
    op.add_column('trips', sa.Column('grand_total', sa.Numeric(precision=12, scale=2), nullable=True))
    op.create_foreign_key('fk_trips_package_id', 'trips', 'trip_packages', ['package_id'], ['id'], ondelete='SET NULL')
    op.create_index('ix_trips_package_id', 'trips', ['package_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_trips_package_id', table_name='trips')
    op.drop_constraint('fk_trips_package_id', 'trips', type_='foreignkey')
    op.drop_column('trips', 'grand_total')
    op.drop_column('trips', 'parking_amount')
    op.drop_column('trips', 'toll_amount')
    op.drop_column('trips', 'state_tax_amount')
    op.drop_column('trips', 'permit_amount')
    op.drop_column('trips', 'night_charges')
    op.drop_column('trips', 'driver_bata')
    op.drop_column('trips', 'extra_hour_amount')
    op.drop_column('trips', 'extra_km_amount')
    op.drop_column('trips', 'package_amount')
    op.drop_column('trips', 'extra_hours')
    op.drop_column('trips', 'extra_km')
    op.drop_column('trips', 'days_used')
    op.drop_column('trips', 'hours_used')
    op.drop_column('trips', 'included_hours')
    op.drop_column('trips', 'included_km')
    op.drop_column('trips', 'end_place')
    op.drop_column('trips', 'start_place')
    op.drop_column('trips', 'trip_date')
    op.drop_column('trips', 'package_name')
    op.drop_column('trips', 'package_id')
