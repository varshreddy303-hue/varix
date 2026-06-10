"""profit_engine_tables

Revision ID: b7c1e3a5d2f4
Revises: 98ef6543c1bd
Create Date: 2026-06-06 21:15:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b7c1e3a5d2f4'
down_revision = '98ef6543c1bd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'trip_profit_summary',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('trip_id', sa.BigInteger(), nullable=False),
        sa.Column('vehicle_id', sa.BigInteger(), nullable=False),
        sa.Column('trip_revenue', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('total_expense', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('trip_profit', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('profit_date', sa.Date(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('month', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['trip_id'], ['trips.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('trip_id', name='uq_trip_profit_summary_trip'),
    )
    op.create_index('ix_trip_profit_summary_org_trip', 'trip_profit_summary', ['organization_id', 'trip_id'], unique=False)
    op.create_index('ix_trip_profit_summary_org_vehicle', 'trip_profit_summary', ['organization_id', 'vehicle_id'], unique=False)
    op.create_index('ix_trip_profit_summary_profit_date', 'trip_profit_summary', ['profit_date'], unique=False)
    op.create_index('ix_trip_profit_summary_year_month', 'trip_profit_summary', ['year', 'month'], unique=False)

    op.create_table(
        'vehicle_daily_profit',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('vehicle_id', sa.BigInteger(), nullable=False),
        sa.Column('profit_date', sa.Date(), nullable=False),
        sa.Column('total_revenue', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('total_expense', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('total_profit', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('vehicle_id', 'profit_date', name='uq_vehicle_daily_profit_date'),
    )
    op.create_index('ix_vehicle_daily_profit_org_vehicle', 'vehicle_daily_profit', ['organization_id', 'vehicle_id'], unique=False)
    op.create_index('ix_vehicle_daily_profit_profit_date', 'vehicle_daily_profit', ['profit_date'], unique=False)

    op.create_table(
        'vehicle_monthly_profit',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('vehicle_id', sa.BigInteger(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('month', sa.Integer(), nullable=False),
        sa.Column('total_revenue', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('total_expense', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('total_profit', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('vehicle_id', 'year', 'month', name='uq_vehicle_monthly_profit_period'),
    )
    op.create_index('ix_vehicle_monthly_profit_org_vehicle', 'vehicle_monthly_profit', ['organization_id', 'vehicle_id'], unique=False)
    op.create_index('ix_vehicle_monthly_profit_year_month', 'vehicle_monthly_profit', ['year', 'month'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_vehicle_monthly_profit_year_month', table_name='vehicle_monthly_profit')
    op.drop_index('ix_vehicle_monthly_profit_org_vehicle', table_name='vehicle_monthly_profit')
    op.drop_table('vehicle_monthly_profit')
    op.drop_index('ix_vehicle_daily_profit_profit_date', table_name='vehicle_daily_profit')
    op.drop_index('ix_vehicle_daily_profit_org_vehicle', table_name='vehicle_daily_profit')
    op.drop_table('vehicle_daily_profit')
    op.drop_index('ix_trip_profit_summary_year_month', table_name='trip_profit_summary')
    op.drop_index('ix_trip_profit_summary_profit_date', table_name='trip_profit_summary')
    op.drop_index('ix_trip_profit_summary_org_vehicle', table_name='trip_profit_summary')
    op.drop_index('ix_trip_profit_summary_org_trip', table_name='trip_profit_summary')
    op.drop_table('trip_profit_summary')
