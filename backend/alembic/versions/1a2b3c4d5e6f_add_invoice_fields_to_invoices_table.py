"""Add invoice trip relation and invoice fields

Revision ID: 1a2b3c4d5e6f
Revises: b7c1e3a5d2f4
Create Date: 2026-06-06 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = '1a2b3c4d5e6f'
down_revision = 'b7c1e3a5d2f4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'invoices',
        sa.Column('trip_id', sa.BigInteger(), sa.ForeignKey('trips.id', ondelete='CASCADE'), nullable=True),
    )
    op.add_column(
        'invoices',
        sa.Column('invoice_number', sa.String(length=128), nullable=True),
    )
    op.add_column(
        'invoices',
        sa.Column('invoice_date', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    op.add_column(
        'invoices',
        sa.Column('subtotal', sa.Numeric(12, 2), server_default='0', nullable=False),
    )
    op.add_column(
        'invoices',
        sa.Column('tax_amount', sa.Numeric(12, 2), server_default='0', nullable=False),
    )
    op.add_column(
        'invoices',
        sa.Column('total_amount', sa.Numeric(12, 2), server_default='0', nullable=False),
    )

    op.create_unique_constraint('uq_invoice_org_number', 'invoices', ['organization_id', 'invoice_number'])
    op.create_unique_constraint('uq_invoices_trip_id', 'invoices', ['trip_id'])
    op.create_index('ix_invoices_org_trip', 'invoices', ['organization_id', 'trip_id'])

    op.drop_column('invoices', 'amount_cents')
    op.drop_column('invoices', 'amount_paid_cents')
    op.drop_column('invoices', 'currency')


def downgrade() -> None:
    op.add_column(
        'invoices',
        sa.Column('currency', sa.String(length=8), nullable=False, server_default='INR'),
    )
    op.add_column(
        'invoices',
        sa.Column('amount_paid_cents', sa.BigInteger(), nullable=False, server_default='0'),
    )
    op.add_column(
        'invoices',
        sa.Column('amount_cents', sa.BigInteger(), nullable=False, server_default='0'),
    )

    op.drop_index('ix_invoices_org_trip', table_name='invoices')
    op.drop_constraint('uq_invoices_trip_id', 'invoices', type_='unique')
    op.drop_constraint('uq_invoice_org_number', 'invoices', type_='unique')

    op.drop_column('invoices', 'total_amount')
    op.drop_column('invoices', 'tax_amount')
    op.drop_column('invoices', 'subtotal')
    op.drop_column('invoices', 'invoice_date')
    op.drop_column('invoices', 'invoice_number')
    op.drop_column('invoices', 'trip_id')
