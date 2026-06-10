from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..models import AuditLog, MaintenanceSchedule, User, Vehicle
from ..repositories import booking_repository, maintenance_repository, vehicle_repository
from ..schemas.maintenance import MaintenanceScheduleCreate, MaintenanceScheduleUpdate
from .audit_utils import serialize_audit_changes


def _create_audit_log(db: Session, user: User, organization_id: str, entity_id: int, action: str, changes: dict) -> AuditLog:
    audit = AuditLog(
        organization_id=organization_id,
        user_id=user.id,
        entity_type='maintenance_schedule',
        entity_id=entity_id,
        action=action,
        changes=serialize_audit_changes(changes),
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit


def _validate_schedule_dates(start_date: datetime, end_date: datetime) -> None:
    if end_date <= start_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='end_date must be after start_date')


def create_maintenance_schedule_service(db: Session, current_user: User, payload: MaintenanceScheduleCreate) -> MaintenanceSchedule:
    organization_id = str(current_user.organization_id)
    vehicle = vehicle_repository.get_vehicle_by_id(db, payload.vehicle_id, organization_id)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Vehicle not found')

    _validate_schedule_dates(payload.start_date, payload.end_date)

    if not booking_repository.is_vehicle_available(
        db,
        payload.vehicle_id,
        payload.start_date,
        payload.end_date,
        organization_id=organization_id,
    ):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Vehicle has a booking during the requested maintenance window')

    if maintenance_repository.get_overlapping_maintenance(
        db,
        payload.vehicle_id,
        payload.start_date,
        payload.end_date,
        organization_id=organization_id,
    ):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Vehicle already has maintenance scheduled during the requested window')

    schedule = MaintenanceSchedule(
        organization_id=current_user.organization_id,
        vehicle_id=payload.vehicle_id,
        start_date=payload.start_date,
        end_date=payload.end_date,
        reason=payload.reason,
        status=payload.status or 'scheduled',
    )

    schedule = maintenance_repository.create_maintenance_schedule(db, schedule)
    maintenance_repository.upsert_maintenance_calendar_event(db, schedule)
    _create_audit_log(db, current_user, organization_id, schedule.id, 'create', payload.dict(exclude_none=True))
    return schedule


def list_maintenance_schedules_service(
    db: Session,
    current_user: User,
    vehicle_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> List[MaintenanceSchedule]:
    organization_id = str(current_user.organization_id)
    return maintenance_repository.list_maintenance_schedules(
        db,
        organization_id=organization_id,
        vehicle_id=vehicle_id,
        start_date=start_date,
        end_date=end_date,
    )


def update_maintenance_schedule_service(
    db: Session,
    maintenance_id: int,
    current_user: User,
    payload: MaintenanceScheduleUpdate,
) -> MaintenanceSchedule:
    organization_id = str(current_user.organization_id)
    schedule = maintenance_repository.get_maintenance_by_id(db, maintenance_id, organization_id)
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Maintenance schedule not found')

    update_data = {k: v for k, v in payload.dict().items() if v is not None}
    if 'start_date' in update_data or 'end_date' in update_data:
        start_date = update_data.get('start_date', schedule.start_date)
        end_date = update_data.get('end_date', schedule.end_date)
        _validate_schedule_dates(start_date, end_date)

        if not booking_repository.is_vehicle_available(
            db,
            schedule.vehicle_id,
            start_date,
            end_date,
            organization_id=organization_id,
        ):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Vehicle has a booking during the requested maintenance window')

        if maintenance_repository.get_overlapping_maintenance(
            db,
            schedule.vehicle_id,
            start_date,
            end_date,
            organization_id=organization_id,
            exclude_maintenance_id=schedule.id,
        ):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Vehicle already has maintenance scheduled during the requested window')

    schedule = maintenance_repository.update_maintenance_schedule(db, schedule, update_data)
    maintenance_repository.upsert_maintenance_calendar_event(db, schedule)
    _create_audit_log(db, current_user, organization_id, schedule.id, 'update', update_data)
    return schedule
