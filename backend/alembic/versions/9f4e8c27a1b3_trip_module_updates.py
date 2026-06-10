"""trip_module_updates

Revision ID: 9f4e8c27a1b3
Revises: 4ad3496eda1a
Create Date: 2026-06-06 19:45:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '9f4e8c27a1b3'
down_revision = '4ad3496eda1a'
branch_labels = None
depends_on = None

trip_status_enum = postgresql.ENUM(
    'pending',
    'ongoing',
    'completed',
    'cancelled',
    name='trip_status',
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    trip_status_enum.create(bind, checkfirst=True)

    op.add_column('trips', sa.Column('vehicle_id', sa.BigInteger(), nullable=True))
    op.add_column('trips', sa.Column('start_km', sa.BigInteger(), nullable=False, server_default='0'))
    op.add_column('trips', sa.Column('end_km', sa.BigInteger(), nullable=True))
    op.add_column('trips', sa.Column('trip_revenue', sa.Numeric(precision=12, scale=2), nullable=True))
    op.add_column(
        'trips',
        sa.Column(
            'status',
            trip_status_enum,
            nullable=False,
            server_default=sa.text("'pending'"),
        ),
    )
    op.add_column('trips', sa.Column('notes', sa.Text(), nullable=True))

    op.execute(
        """
        UPDATE trips
        SET vehicle_id = bookings.vehicle_id
        FROM bookings
        WHERE trips.booking_id = bookings.id
        """
    )

    op.alter_column('trips', 'vehicle_id', existing_type=sa.BigInteger(), nullable=False)
    op.alter_column('trips', 'start_km', existing_type=sa.BigInteger(), server_default=None)

    op.create_foreign_key(
        'fk_trips_vehicle_id_vehicles',
        'trips',
        'vehicles',
        ['vehicle_id'],
        ['id'],
        ondelete='RESTRICT',
    )

    op.create_index('ix_trips_booking_id', 'trips', ['booking_id'], unique=False)
    op.create_index('ix_trips_vehicle_id', 'trips', ['vehicle_id'], unique=False)
    op.create_index('ix_trips_status', 'trips', ['status'], unique=False)
    op.create_index('ix_trips_org_booking', 'trips', ['organization_id', 'booking_id'], unique=False)
    op.create_index('ix_trips_org_vehicle', 'trips', ['organization_id', 'vehicle_id'], unique=False)

    op.drop_constraint('trips_booking_id_key', 'trips', type_='unique')
    op.drop_column('trips', 'fare')
    op.drop_column('trips', 'telemetry')


def downgrade() -> None:
    op.add_column('trips', sa.Column('telemetry', sa.JSON(), nullable=True))
    op.add_column('trips', sa.Column('fare', sa.Numeric(precision=12, scale=2), nullable=True))
    op.create_unique_constraint('trips_booking_id_key', 'trips', ['booking_id'])

    op.drop_index('ix_trips_org_vehicle', table_name='trips')
    op.drop_index('ix_trips_org_booking', table_name='trips')
    op.drop_index('ix_trips_status', table_name='trips')
    op.drop_index('ix_trips_vehicle_id', table_name='trips')
    op.drop_index('ix_trips_booking_id', table_name='trips')

    op.drop_constraint('fk_trips_vehicle_id_vehicles', 'trips', type_='foreignkey')
    op.drop_column('trips', 'notes')
    op.drop_column('trips', 'status')
    op.drop_column('trips', 'trip_revenue')
    op.drop_column('trips', 'end_km')
    op.drop_column('trips', 'start_km')
    op.drop_column('trips', 'vehicle_id')

    bind = op.get_bind()
    trip_status_enum.drop(bind, checkfirst=True)
