"""create_expenses_table

Revision ID: 98ef6543c1bd
Revises: 4ad3496eda1a
Create Date: 2026-06-06 20:30:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '98ef6543c1bd'
down_revision = '4ad3496eda1a'
branch_labels = None
depends_on = None

expense_category_enum = postgresql.ENUM(
    'fuel',
    'toll',
    'parking',
    'maintenance',
    'other',
    name='expense_category',
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    expense_category_enum.create(bind, checkfirst=True)

    op.create_table(
        'expenses',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('trip_id', sa.BigInteger(), sa.ForeignKey('trips.id', ondelete='CASCADE'), nullable=False),
        sa.Column('vehicle_id', sa.BigInteger(), sa.ForeignKey('vehicles.id', ondelete='RESTRICT'), nullable=False),
        sa.Column(
            'category',
            expense_category_enum,
            nullable=False,
        ),
        sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('expense_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
    )

    op.create_index(op.f('ix_expenses_organization_id'), 'expenses', ['organization_id'], unique=False)
    op.create_index('ix_expenses_trip_id', 'expenses', ['trip_id'], unique=False)
    op.create_index('ix_expenses_vehicle_id', 'expenses', ['vehicle_id'], unique=False)
    op.create_index('ix_expenses_category', 'expenses', ['category'], unique=False)
    op.create_index('ix_expenses_expense_date', 'expenses', ['expense_date'], unique=False)
    op.create_index('ix_expenses_org_trip', 'expenses', ['organization_id', 'trip_id'], unique=False)
    op.create_index('ix_expenses_org_vehicle', 'expenses', ['organization_id', 'vehicle_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_expenses_org_vehicle', table_name='expenses')
    op.drop_index('ix_expenses_org_trip', table_name='expenses')
    op.drop_index('ix_expenses_expense_date', table_name='expenses')
    op.drop_index('ix_expenses_category', table_name='expenses')
    op.drop_index('ix_expenses_vehicle_id', table_name='expenses')
    op.drop_index('ix_expenses_trip_id', table_name='expenses')
    op.drop_index(op.f('ix_expenses_organization_id'), table_name='expenses')
    op.drop_table('expenses')

    bind = op.get_bind()
    expense_category_enum.drop(bind, checkfirst=True)
