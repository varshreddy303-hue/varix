"""Merge migration heads and add booking_id to expenses

Revision ID: z9a8b7c6d5e4
Revises: ('e5d4c3b2a1f1', 'f3g4h5i6j7k8')
Create Date: 2026-06-09 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = 'z9a8b7c6d5e4'
down_revision = ('e5d4c3b2a1f1', 'f3g4h5i6j7k8')
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('expenses', 'trip_id', existing_type=sa.BigInteger(), nullable=True)
    op.add_column('expenses', sa.Column('booking_id', sa.BigInteger(), nullable=True))
    op.create_foreign_key('fk_expenses_booking_id_bookings', 'expenses', 'bookings', ['booking_id'], ['id'], ondelete='SET NULL')
    op.create_index('ix_expenses_booking_id', 'expenses', ['booking_id'], unique=False)
    op.create_index('ix_expenses_org_booking', 'expenses', ['organization_id', 'booking_id'], unique=False)


def downgrade() -> None:
    op.drop_constraint('fk_expenses_booking_id_bookings', 'expenses', type_='foreignkey')
    op.drop_index('ix_expenses_org_booking', table_name='expenses')
    op.drop_index('ix_expenses_booking_id', table_name='expenses')
    op.drop_column('expenses', 'booking_id')
    op.alter_column('expenses', 'trip_id', existing_type=sa.BigInteger(), nullable=False)
