from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from ..models import (
    Booking,
    CalendarEventStatusEnum,
    CalendarEventTypeEnum,
    MaintenanceSchedule,
    VehicleCalendarEvent,
    MaintenanceStatusEnum,
)


def get_maintenance_by_id(db: Session, maintenance_id: int, organization_id: Optional[str] = None) -> Optional[MaintenanceSchedule]:
    query = db.query(MaintenanceSchedule).filter(MaintenanceSchedule.id == maintenance_id)
    if organization_id:
        query = query.filter(MaintenanceSchedule.organization_id == organization_id)
    return query.first()


def list_maintenance_schedules(
    db: Session,
    organization_id: Optional[str] = None,
    vehicle_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    offset: int = 0,
    limit: int = 50,
) -> List[MaintenanceSchedule]:
    query = db.query(MaintenanceSchedule)
    if organization_id:
        query = query.filter(MaintenanceSchedule.organization_id == organization_id)
    if vehicle_id is not None:
        query = query.filter(MaintenanceSchedule.vehicle_id == vehicle_id)
    if start_date:
        query = query.filter(MaintenanceSchedule.end_date >= start_date)
    if end_date:
        query = query.filter(MaintenanceSchedule.start_date <= end_date)
    return query.order_by(MaintenanceSchedule.start_date.desc()).offset(offset).limit(limit).all()


def create_maintenance_schedule(db: Session, schedule: MaintenanceSchedule) -> MaintenanceSchedule:
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule


def update_maintenance_schedule(db: Session, schedule: MaintenanceSchedule, values: dict) -> MaintenanceSchedule:
    for key, value in values.items():
        setattr(schedule, key, value)
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule


def get_overlapping_maintenance(
    db: Session,
    vehicle_id: int,
    start_date: datetime,
    end_date: datetime,
    organization_id: Optional[str] = None,
    exclude_maintenance_id: Optional[int] = None,
) -> bool:
    query = db.query(MaintenanceSchedule).filter(
        MaintenanceSchedule.vehicle_id == vehicle_id,
        MaintenanceSchedule.status != MaintenanceStatusEnum.CANCELLED,
        MaintenanceSchedule.start_date <= end_date,
        MaintenanceSchedule.end_date >= start_date,
    )
    if organization_id:
        query = query.filter(MaintenanceSchedule.organization_id == organization_id)
    if exclude_maintenance_id is not None:
        query = query.filter(MaintenanceSchedule.id != exclude_maintenance_id)
    return db.query(query.exists()).scalar()


def get_calendar_event_by_booking(db: Session, booking_id: int, organization_id: Optional[str] = None) -> Optional[VehicleCalendarEvent]:
    query = db.query(VehicleCalendarEvent).filter(VehicleCalendarEvent.booking_id == booking_id)
    if organization_id:
        query = query.filter(VehicleCalendarEvent.organization_id == organization_id)
    return query.first()


def get_calendar_event_by_maintenance(db: Session, maintenance_id: int, organization_id: Optional[str] = None) -> Optional[VehicleCalendarEvent]:
    query = db.query(VehicleCalendarEvent).filter(VehicleCalendarEvent.maintenance_id == maintenance_id)
    if organization_id:
        query = query.filter(VehicleCalendarEvent.organization_id == organization_id)
    return query.first()


def create_calendar_event(db: Session, event: VehicleCalendarEvent) -> VehicleCalendarEvent:
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def update_calendar_event(db: Session, event: VehicleCalendarEvent, values: dict) -> VehicleCalendarEvent:
    for key, value in values.items():
        setattr(event, key, value)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def list_calendar_events(
    db: Session,
    organization_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    offset: int = 0,
    limit: int = 200,
) -> List[VehicleCalendarEvent]:
    query = db.query(VehicleCalendarEvent)
    if organization_id:
        query = query.filter(VehicleCalendarEvent.organization_id == organization_id)
    if start_date:
        query = query.filter(VehicleCalendarEvent.end_date >= start_date)
    if end_date:
        query = query.filter(VehicleCalendarEvent.start_date <= end_date)
    return query.order_by(VehicleCalendarEvent.start_date.asc()).offset(offset).limit(limit).all()


def upsert_booking_calendar_event(db: Session, booking: Booking) -> VehicleCalendarEvent:
    existing = get_calendar_event_by_booking(db, booking.id, str(booking.organization_id))
    values = {
        'vehicle_id': booking.vehicle_id,
        'booking_id': booking.id,
        'maintenance_id': None,
        'title': f'Booking #{booking.id}',
        'event_type': CalendarEventTypeEnum.BOOKING,
        'status': booking.status,
        'start_date': booking.start_date,
        'end_date': booking.end_date,
    }
    if existing:
        return update_calendar_event(db, existing, values)

    event = VehicleCalendarEvent(
        organization_id=booking.organization_id,
        vehicle_id=booking.vehicle_id,
        booking_id=booking.id,
        title=values['title'],
        event_type=values['event_type'],
        status=values['status'],
        start_date=values['start_date'],
        end_date=values['end_date'],
    )
    return create_calendar_event(db, event)


def upsert_maintenance_calendar_event(db: Session, schedule: MaintenanceSchedule) -> VehicleCalendarEvent:
    existing = get_calendar_event_by_maintenance(db, schedule.id, str(schedule.organization_id))
    values = {
        'vehicle_id': schedule.vehicle_id,
        'booking_id': None,
        'maintenance_id': schedule.id,
        'title': f'Maintenance #{schedule.id}',
        'event_type': CalendarEventTypeEnum.MAINTENANCE,
        'status': schedule.status,
        'start_date': schedule.start_date,
        'end_date': schedule.end_date,
    }
    if existing:
        return update_calendar_event(db, existing, values)

    event = VehicleCalendarEvent(
        organization_id=schedule.organization_id,
        vehicle_id=schedule.vehicle_id,
        maintenance_id=schedule.id,
        title=values['title'],
        event_type=values['event_type'],
        status=values['status'],
        start_date=values['start_date'],
        end_date=values['end_date'],
    )
    return create_calendar_event(db, event)
