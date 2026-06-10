import calendar
from datetime import datetime, date, timedelta
from typing import Any, Dict, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..models import AuditLog, User, Vehicle
from ..repositories import booking_repository, maintenance_repository, vehicle_repository
from ..schemas.vehicle import VehicleCreate, VehicleUpdate
from .audit_utils import serialize_audit_changes


def _create_audit_log(db: Session, user: User, organization_id: str, entity_id: int, action: str, changes: dict) -> AuditLog:
    audit = AuditLog(
        organization_id=organization_id,
        user_id=user.id,
        entity_type="vehicle",
        entity_id=entity_id,
        action=action,
        changes=serialize_audit_changes(changes),
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit


def _calculate_next_emi_due_datetime(current_date: date, due_day: int) -> Optional[datetime]:
    if due_day < 1 or due_day > 31:
        return None

    year = current_date.year
    month = current_date.month
    if due_day < current_date.day:
        month += 1
        if month > 12:
            month = 1
            year += 1

    last_day = calendar.monthrange(year, month)[1]
    selected_day = min(due_day, last_day)
    return datetime(year, month, selected_day)


def _normalize_expiry_date(value: Optional[datetime | date]) -> Optional[date]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    return value


def _find_vehicle_document_conflict(vehicle: Vehicle, start_date: datetime, end_date: datetime) -> Optional[str]:
    start_day = _normalize_expiry_date(start_date)
    end_day = _normalize_expiry_date(end_date)

    expiries = [
        ('insurance', vehicle.insurance_expiry_date),
        ('permit', vehicle.permit_expiry_date),
        ('fitness certificate', vehicle.fc_expiry_date),
        ('pollution', vehicle.pollution_expiry_date),
        ('road tax', vehicle.road_tax_expiry_date),
        ('GPS subscription', vehicle.gps_subscription_expiry_date),
    ]

    for label, expiry_date in expiries:
        expiry_day = _normalize_expiry_date(expiry_date)
        if expiry_day is None:
            continue
        if start_day <= expiry_day <= end_day:
            return f'{label.title()} expires during the requested window'
    return None


def create_vehicle_service(db: Session, current_user: User, payload: VehicleCreate) -> Vehicle:
    organization_id = str(current_user.organization_id)
    if vehicle_repository.get_vehicle_by_number(db, payload.vehicle_number, organization_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Vehicle number already exists for this organization")

    vehicle = Vehicle(
        organization_id=current_user.organization_id,
        vehicle_number=payload.vehicle_number,
        vehicle_type=payload.vehicle_type,
        make=payload.make,
        model=payload.model,
        seating_capacity=payload.seating_capacity,
        fuel_type=payload.fuel_type,
        registration_date=payload.registration_date,
        insurance_expiry_date=payload.insurance_expiry_date,
        permit_expiry_date=payload.permit_expiry_date,
        fc_expiry_date=payload.fc_expiry_date,
        pollution_expiry_date=payload.pollution_expiry_date,
        road_tax_expiry_date=payload.road_tax_expiry_date,
        gps_subscription_expiry_date=payload.gps_subscription_expiry_date,
        service_due_date=payload.service_due_date,
        tyre_change_due_date=payload.tyre_change_due_date,
        battery_change_due_date=payload.battery_change_due_date,
        loan_closure_date=payload.loan_closure_date,
        purchase_price=payload.purchase_price,
        emi_amount=payload.emi_amount,
        emi_due_day=payload.emi_due_day,
        is_active=payload.is_active if payload.is_active is not None else True,
    )

    vehicle = vehicle_repository.create_vehicle(db, vehicle)
    _create_audit_log(db, current_user, organization_id, vehicle.id, "create", payload.dict(exclude_none=True))
    return vehicle


def get_vehicle_service(db: Session, vehicle_id: int, current_user: User) -> Vehicle:
    organization_id = str(current_user.organization_id)
    vehicle = vehicle_repository.get_vehicle_by_id(db, vehicle_id, organization_id)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
    return vehicle


def update_vehicle_service(db: Session, vehicle_id: int, current_user: User, payload: VehicleUpdate) -> Vehicle:
    organization_id = str(current_user.organization_id)
    vehicle = vehicle_repository.get_vehicle_by_id(db, vehicle_id, organization_id)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")

    if payload.vehicle_number and payload.vehicle_number != vehicle.vehicle_number:
        if vehicle_repository.get_vehicle_by_number(db, payload.vehicle_number, organization_id):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Vehicle number already exists for this organization")

    update_data: Dict[str, Any] = {k: v for k, v in payload.dict().items() if v is not None}
    vehicle = vehicle_repository.update_vehicle(db, vehicle, update_data)
    _create_audit_log(db, current_user, organization_id, vehicle.id, "update", update_data)
    return vehicle


def delete_vehicle_service(db: Session, vehicle_id: int, current_user: User) -> None:
    organization_id = str(current_user.organization_id)
    vehicle = vehicle_repository.get_vehicle_by_id(db, vehicle_id, organization_id)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
    vehicle_repository.soft_delete_vehicle(db, vehicle)
    _create_audit_log(db, current_user, organization_id, vehicle.id, "delete", {"deleted_at": datetime.utcnow().isoformat()})


def list_vehicles_service(
    db: Session,
    current_user: User,
    vehicle_number: Optional[str] = None,
    vehicle_type: Optional[str] = None,
    make: Optional[str] = None,
    model: Optional[str] = None,
    fuel_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    page: int = 1,
    page_size: int = 25,
) -> Tuple[list[Vehicle], int]:
    if page < 1 or page_size < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid pagination parameters")

    organization_id = str(current_user.organization_id)
    offset = (page - 1) * page_size
    return vehicle_repository.list_vehicles(
        db,
        organization_id=organization_id,
        vehicle_number=vehicle_number,
        vehicle_type=vehicle_type,
        make=make,
        model=model,
        fuel_type=fuel_type,
        is_active=is_active,
        offset=offset,
        limit=page_size,
    )


def list_expiring_documents_service(db: Session, current_user: User, within_days: int = 30) -> list[Vehicle]:
    if within_days < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Window must be at least 1 day")
    organization_id = str(current_user.organization_id)
    return vehicle_repository.list_expiring_documents(db, organization_id, within_days)


def check_vehicle_availability_service(
    db: Session,
    current_user: User,
    vehicle_id: int,
    start_date: datetime,
    end_date: datetime,
    exclude_booking_id: Optional[int] = None,
) -> tuple[bool, Optional[str]]:
    organization_id = str(current_user.organization_id)
    vehicle = vehicle_repository.get_vehicle_by_id(db, vehicle_id, organization_id)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Vehicle not found')

    reason = _find_vehicle_document_conflict(vehicle, start_date, end_date)
    if reason:
        return False, reason

    if not booking_repository.is_vehicle_available(
        db,
        vehicle_id,
        start_date,
        end_date,
        organization_id=organization_id,
        exclude_booking_id=exclude_booking_id,
    ):
        return False, 'Vehicle has a booking during the requested window'

    if maintenance_repository.get_overlapping_maintenance(
        db,
        vehicle_id,
        start_date,
        end_date,
        organization_id=organization_id,
    ):
        return False, 'Vehicle has maintenance scheduled during the requested window'

    return True, None


def list_upcoming_emi_service(db: Session, current_user: User, within_days: int = 30) -> list[Vehicle]:
    if within_days < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Window must be at least 1 day")
    organization_id = str(current_user.organization_id)
    vehicles = vehicle_repository.list_vehicles_for_emi(db, organization_id)

    today = datetime.utcnow().date()
    upcoming: list[Vehicle] = []
    for vehicle in vehicles:
        if vehicle.emi_due_day is None:
            continue
        next_due = _calculate_next_emi_due_datetime(today, vehicle.emi_due_day)
        if not next_due:
            continue

        days_until_due = (next_due.date() - today).days
        if 0 <= days_until_due <= within_days:
            setattr(vehicle, "next_emi_due_date", next_due)
            upcoming.append(vehicle)

    return upcoming
