"""add_trip_rate_fields

Revision ID: a1b2c3d4e5f6
Revises: f2f3e4d5c6b7
Create Date: 2026-06-08 16:30:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'd1e2f3g4h5i6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('trips', sa.Column('extra_km_rate', sa.Numeric(precision=12, scale=2), nullable=True))
    op.add_column('trips', sa.Column('extra_hour_rate', sa.Numeric(precision=12, scale=2), nullable=True))
    op.add_column('trips', sa.Column('minimum_km_per_day', sa.Integer(), nullable=True))
    op.add_column('trips', sa.Column('km_rate', sa.Numeric(precision=12, scale=2), nullable=True))


def downgrade() -> None:
    op.drop_column('trips', 'km_rate')
    op.drop_column('trips', 'minimum_km_per_day')
    op.drop_column('trips', 'extra_hour_rate')
    op.drop_column('trips', 'extra_km_rate')
