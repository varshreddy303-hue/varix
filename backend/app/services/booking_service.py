from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..models import AuditLog, Booking, Customer, User, Vehicle
from ..repositories import booking_repository, customer_repository, maintenance_repository, vehicle_repository
from . import vehicle_service
from ..schemas.booking import BookingCreate, BookingUpdate
from .audit_utils import serialize_audit_changes


def _create_audit_log(db: Session, user: User, organization_id: str, entity_id: int, action: str, changes: dict) -> AuditLog:
    audit = AuditLog(
        organization_id=organization_id,
        user_id=user.id,
        entity_type="booking",
        entity_id=entity_id,
        action=action,
        changes=serialize_audit_changes(changes),
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit


def _assert_customer_and_vehicle_belong_to_org(db: Session, organization_id: str, customer_id: Optional[int], vehicle_id: int) -> tuple[Optional[Customer], Vehicle]:
    if customer_id is not None:
        customer = customer_repository.get_customer_by_id(db, customer_id, organization_id)
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    else:
        customer = None

    vehicle = vehicle_repository.get_vehicle_by_id(db, vehicle_id, organization_id)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")

    return customer, vehicle


def _validate_booking_dates(start_date: datetime, end_date: datetime) -> None:
    if end_date <= start_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="end_date must be after start_date")


def create_booking_service(db: Session, current_user: User, payload: BookingCreate) -> Booking:
    organization_id = str(current_user.organization_id)
    _assert_customer_and_vehicle_belong_to_org(db, organization_id, payload.customer_id, payload.vehicle_id)
    _validate_booking_dates(payload.start_date, payload.end_date)

    available, reason = vehicle_service.check_vehicle_availability_service(
        db,
        current_user,
        payload.vehicle_id,
        payload.start_date,
        payload.end_date,
    )
    if not available:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=reason or "Vehicle is not available for the requested dates")

    booking = Booking(
        organization_id=current_user.organization_id,
        customer_id=payload.customer_id,
        customer_name=payload.customer_name,
        customer_company=payload.customer_company,
        customer_phone=payload.customer_phone,
        customer_email=payload.customer_email,
        customer_gst_number=payload.customer_gst_number,
        customer_city=payload.customer_city,
        customer_notes=payload.customer_notes,
        vehicle_id=payload.vehicle_id,
        pickup_location=payload.pickup_location,
        destination=payload.destination,
        start_date=payload.start_date,
        end_date=payload.end_date,
        booking_amount=payload.booking_amount,
        status=payload.status or "pending",
    )
    booking = booking_repository.create_booking(db, booking)
    maintenance_repository.upsert_booking_calendar_event(db, booking)
    _create_audit_log(db, current_user, organization_id, booking.id, "create", payload.dict(exclude_none=True))
    return booking


def get_booking_service(db: Session, booking_id: int, current_user: User) -> Booking:
    organization_id = str(current_user.organization_id)
    booking = booking_repository.get_booking_by_id(db, booking_id, organization_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    return booking


def update_booking_service(db: Session, booking_id: int, current_user: User, payload: BookingUpdate) -> Booking:
    organization_id = str(current_user.organization_id)
    booking = booking_repository.get_booking_by_id(db, booking_id, organization_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    update_data: Dict[str, Any] = {k: v for k, v in payload.dict().items() if v is not None}
    if "start_date" in update_data or "end_date" in update_data:
        start_date = update_data.get("start_date", booking.start_date)
        end_date = update_data.get("end_date", booking.end_date)
        _validate_booking_dates(start_date, end_date)

        available, reason = vehicle_service.check_vehicle_availability_service(
            db,
            current_user,
            update_data.get("vehicle_id", booking.vehicle_id),
            start_date,
            end_date,
            exclude_booking_id=booking.id,
        )
        if not available:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=reason or "Vehicle is not available for the requested dates")

    if "customer_id" in update_data or "vehicle_id" in update_data:
        customer_id = update_data.get("customer_id", booking.customer_id)
        vehicle_id = update_data.get("vehicle_id", booking.vehicle_id)
        _assert_customer_and_vehicle_belong_to_org(db, organization_id, customer_id, vehicle_id)

    booking = booking_repository.update_booking(db, booking, update_data)
    maintenance_repository.upsert_booking_calendar_event(db, booking)
    _create_audit_log(db, current_user, organization_id, booking.id, "update", update_data)
    return booking


def cancel_booking_service(db: Session, booking_id: int, current_user: User) -> Booking:
    organization_id = str(current_user.organization_id)
    booking = booking_repository.get_booking_by_id(db, booking_id, organization_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    booking = booking_repository.cancel_booking(db, booking)
    maintenance_repository.upsert_booking_calendar_event(db, booking)
    _create_audit_log(db, current_user, organization_id, booking.id, "cancel", {"status": "cancelled"})
    return booking


def list_bookings_service(
    db: Session,
    current_user: User,
    customer_id: Optional[int] = None,
    vehicle_id: Optional[int] = None,
    status: Optional[str] = None,
    pickup_location: Optional[str] = None,
    destination: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 25,
) -> Tuple[list[Booking], int]:
    if page < 1 or page_size < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid pagination parameters")

    organization_id = str(current_user.organization_id)
    offset = (page - 1) * page_size
    return booking_repository.list_bookings(
        db,
        organization_id=organization_id,
        customer_id=customer_id,
        vehicle_id=vehicle_id,
        status=status,
        pickup_location=pickup_location,
        destination=destination,
        start_date=start_date,
        end_date=end_date,
        offset=offset,
        limit=page_size,
    )


def check_vehicle_availability_service(
    db: Session,
    current_user: User,
    vehicle_id: int,
    start_date: datetime,
    end_date: datetime,
) -> bool:
    _validate_booking_dates(start_date, end_date)
    available, _ = vehicle_service.check_vehicle_availability_service(db, current_user, vehicle_id, start_date, end_date)
    return available
