"""Add booking-first customer fields and allow nullable customer_id

Revision ID: 5a6b7c8d9e0f
Revises: a0b1c2d3e4f5
Create Date: 2026-06-09 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5a6b7c8d9e0f'
down_revision = 'a0b1c2d3e4f5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('bookings', 'customer_id', existing_type=sa.Integer(), nullable=True)
    op.add_column('bookings', sa.Column('customer_name', sa.String(length=255), nullable=True))
    op.add_column('bookings', sa.Column('customer_company', sa.String(length=255), nullable=True))
    op.add_column('bookings', sa.Column('customer_phone', sa.String(length=32), nullable=True))
    op.add_column('bookings', sa.Column('customer_email', sa.String(length=255), nullable=True))
    op.add_column('bookings', sa.Column('customer_gst_number', sa.String(length=32), nullable=True))
    op.add_column('bookings', sa.Column('customer_city', sa.String(length=100), nullable=True))
    op.add_column('bookings', sa.Column('customer_notes', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('bookings', 'customer_notes')
    op.drop_column('bookings', 'customer_city')
    op.drop_column('bookings', 'customer_gst_number')
    op.drop_column('bookings', 'customer_email')
    op.drop_column('bookings', 'customer_phone')
    op.drop_column('bookings', 'customer_company')
    op.drop_column('bookings', 'customer_name')
    op.alter_column('bookings', 'customer_id', existing_type=sa.Integer(), nullable=False)
