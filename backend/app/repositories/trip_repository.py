from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from ..models import Trip


def get_trip_by_id(db: Session, trip_id: int, organization_id: Optional[str] = None) -> Optional[Trip]:
    query = db.query(Trip).filter(Trip.id == trip_id)
    if organization_id:
        query = query.filter(Trip.organization_id == organization_id)
    return query.first()


def list_trips(
    db: Session,
    organization_id: Optional[str] = None,
    booking_id: Optional[int] = None,
    vehicle_id: Optional[int] = None,
    status: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    offset: int = 0,
    limit: int = 50,
) -> Tuple[List[Trip], int]:
    query = db.query(Trip)

    if organization_id:
        query = query.filter(Trip.organization_id == organization_id)
    if booking_id is not None:
        query = query.filter(Trip.booking_id == booking_id)
    if vehicle_id is not None:
        query = query.filter(Trip.vehicle_id == vehicle_id)
    if status:
        query = query.filter(Trip.status == status)
    if start_time:
        query = query.filter(Trip.start_time >= start_time)
    if end_time:
        query = query.filter(Trip.end_time <= end_time)

    total = query.count()
    trips = query.order_by(Trip.created_at.desc()).offset(offset).limit(limit).all()
    return trips, total


def create_trip(db: Session, trip: Trip) -> Trip:
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip


def update_trip(db: Session, trip: Trip, values: dict) -> Trip:
    for key, value in values.items():
        setattr(trip, key, value)
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip


def get_active_trip_for_booking(db: Session, booking_id: int, organization_id: Optional[str] = None) -> Optional[Trip]:
    query = db.query(Trip).filter(
        Trip.booking_id == booking_id,
        Trip.status.in_(["pending", "ongoing"]),
    )
    if organization_id:
        query = query.filter(Trip.organization_id == organization_id)
    return query.first()
