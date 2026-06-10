"""Allow nullable trip_id on expenses for booking-based expenses

Revision ID: a0b1c2d3e4f5
Revises: z9a8b7c6d5e4
Create Date: 2026-06-09 00:10:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = 'a0b1c2d3e4f5'
down_revision = 'z9a8b7c6d5e4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('expenses', 'trip_id', existing_type=sa.BigInteger(), nullable=True)


def downgrade() -> None:
    op.alter_column('expenses', 'trip_id', existing_type=sa.BigInteger(), nullable=False)
