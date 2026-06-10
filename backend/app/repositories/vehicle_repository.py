from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from ..models import Vehicle


def get_vehicle_by_id(db: Session, vehicle_id: int, organization_id: Optional[str] = None) -> Optional[Vehicle]:
    query = db.query(Vehicle).filter(Vehicle.id == vehicle_id, Vehicle.deleted_at.is_(None))
    if organization_id:
        query = query.filter(Vehicle.organization_id == organization_id)
    return query.first()


def get_vehicle_by_number(db: Session, vehicle_number: str, organization_id: Optional[str] = None) -> Optional[Vehicle]:
    query = db.query(Vehicle).filter(Vehicle.vehicle_number == vehicle_number, Vehicle.deleted_at.is_(None))
    if organization_id:
        query = query.filter(Vehicle.organization_id == organization_id)
    return query.first()


def create_vehicle(db: Session, vehicle: Vehicle) -> Vehicle:
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle


def update_vehicle(db: Session, vehicle: Vehicle, values: dict) -> Vehicle:
    for key, value in values.items():
        setattr(vehicle, key, value)
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle


def soft_delete_vehicle(db: Session, vehicle: Vehicle) -> Vehicle:
    vehicle.deleted_at = datetime.utcnow()
    vehicle.is_active = False
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle


def list_vehicles(
    db: Session,
    organization_id: Optional[str] = None,
    vehicle_number: Optional[str] = None,
    vehicle_type: Optional[str] = None,
    make: Optional[str] = None,
    model: Optional[str] = None,
    fuel_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    offset: int = 0,
    limit: int = 50,
) -> Tuple[List[Vehicle], int]:
    query = db.query(Vehicle).filter(Vehicle.deleted_at.is_(None))
    if organization_id:
        query = query.filter(Vehicle.organization_id == organization_id)
    if vehicle_number:
        query = query.filter(Vehicle.vehicle_number.ilike(f"%{vehicle_number}%"))
    if vehicle_type:
        query = query.filter(Vehicle.vehicle_type.ilike(f"%{vehicle_type}%"))
    if make:
        query = query.filter(Vehicle.make.ilike(f"%{make}%"))
    if model:
        query = query.filter(Vehicle.model.ilike(f"%{model}%"))
    if fuel_type:
        query = query.filter(Vehicle.fuel_type.ilike(f"%{fuel_type}%"))
    if is_active is not None:
        query = query.filter(Vehicle.is_active.is_(is_active))

    total = query.count()
    vehicles = query.order_by(Vehicle.created_at.desc()).offset(offset).limit(limit).all()
    return vehicles, total


def list_expiring_documents(
    db: Session,
    organization_id: str,
    within_days: int = 30,
) -> List[Vehicle]:
    window_start = datetime.utcnow()
    window_end = window_start + timedelta(days=within_days)

    query = db.query(Vehicle).filter(
        Vehicle.deleted_at.is_(None),
        Vehicle.organization_id == organization_id,
        or_(
            and_(Vehicle.insurance_expiry_date.is_not(None), Vehicle.insurance_expiry_date.between(window_start, window_end)),
            and_(Vehicle.permit_expiry_date.is_not(None), Vehicle.permit_expiry_date.between(window_start, window_end)),
            and_(Vehicle.fc_expiry_date.is_not(None), Vehicle.fc_expiry_date.between(window_start, window_end)),
            and_(Vehicle.pollution_expiry_date.is_not(None), Vehicle.pollution_expiry_date.between(window_start, window_end)),
            and_(Vehicle.road_tax_expiry_date.is_not(None), Vehicle.road_tax_expiry_date.between(window_start, window_end)),
        ),
    )
    return query.order_by(Vehicle.created_at.desc()).all()


def list_vehicles_for_emi(db: Session, organization_id: str) -> List[Vehicle]:
    query = db.query(Vehicle).filter(
        Vehicle.deleted_at.is_(None),
        Vehicle.organization_id == organization_id,
        Vehicle.is_active.is_(True),
        Vehicle.emi_amount.is_not(None),
        Vehicle.emi_due_day.is_not(None),
    )
    return query.order_by(Vehicle.created_at.desc()).all()
