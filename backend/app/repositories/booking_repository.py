from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from ..models import Booking


def get_booking_by_id(db: Session, booking_id: int, organization_id: Optional[str] = None) -> Optional[Booking]:
    query = db.query(Booking).filter(Booking.id == booking_id)
    if organization_id:
        query = query.filter(Booking.organization_id == organization_id)
    return query.first()


def list_bookings(
    db: Session,
    organization_id: Optional[str] = None,
    customer_id: Optional[int] = None,
    vehicle_id: Optional[int] = None,
    status: Optional[str] = None,
    pickup_location: Optional[str] = None,
    destination: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    offset: int = 0,
    limit: int = 50,
) -> Tuple[List[Booking], int]:
    query = db.query(Booking)
    if organization_id:
        query = query.filter(Booking.organization_id == organization_id)
    if customer_id is not None:
        query = query.filter(Booking.customer_id == customer_id)
    if vehicle_id is not None:
        query = query.filter(Booking.vehicle_id == vehicle_id)
    if status:
        query = query.filter(Booking.status == status)
    if pickup_location:
        query = query.filter(Booking.pickup_location.ilike(f"%{pickup_location}%"))
    if destination:
        query = query.filter(Booking.destination.ilike(f"%{destination}%"))
    if start_date:
        query = query.filter(Booking.start_date >= start_date)
    if end_date:
        query = query.filter(Booking.end_date <= end_date)

    total = query.count()
    bookings = query.order_by(Booking.start_date.desc()).offset(offset).limit(limit).all()
    return bookings, total


def create_booking(db: Session, booking: Booking) -> Booking:
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


def update_booking(db: Session, booking: Booking, values: dict) -> Booking:
    for key, value in values.items():
        setattr(booking, key, value)
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


def cancel_booking(db: Session, booking: Booking) -> Booking:
    booking.status = "cancelled"
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


def is_vehicle_available(
    db: Session,
    vehicle_id: int,
    start_date: datetime,
    end_date: datetime,
    organization_id: Optional[str] = None,
    exclude_booking_id: Optional[int] = None,
) -> bool:
    query = db.query(Booking).filter(
        Booking.vehicle_id == vehicle_id,
        Booking.status != "cancelled",
        Booking.start_date <= end_date,
        Booking.end_date >= start_date,
    )
    if organization_id:
        query = query.filter(Booking.organization_id == organization_id)
    if exclude_booking_id is not None:
        query = query.filter(Booking.id != exclude_booking_id)
    return not db.query(query.exists()).scalar()
