from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..models import AuditLog, Booking, Trip, TripPackage, TripStatusEnum, User, Vehicle
from ..repositories import booking_repository, package_repository, trip_repository, vehicle_repository
from . import profit_service
from .audit_utils import serialize_audit_changes
from .invoice_service import InvoiceService
from .trip_calculation_service import calculate_trip_financials
from ..schemas.invoice import InvoiceCreate
from ..schemas.trip import TripCompleteRequest, TripCreate, TripUpdate


def _create_audit_log(db: Session, user: User, organization_id: str, entity_id: int, action: str, changes: dict) -> AuditLog:
    audit = AuditLog(
        organization_id=organization_id,
        user_id=user.id,
        entity_type="trip",
        entity_id=entity_id,
        action=action,
        changes=serialize_audit_changes(changes),
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit


def _assert_booking_belongs_to_org(db: Session, booking_id: int, organization_id: str) -> Booking:
    booking = booking_repository.get_booking_by_id(db, booking_id, organization_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    if booking.status == "cancelled":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot create a trip for a cancelled booking")
    return booking


def _assert_vehicle_matches_booking(booking: Booking, vehicle_id: int) -> None:
    if booking.vehicle_id != vehicle_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vehicle must match the booking vehicle")


def _validate_distance(start_km: int, end_km: Optional[int]) -> None:
    if end_km is not None and end_km < start_km:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="end_km must be greater than or equal to start_km")


def _validate_time_order(start_time: Optional[datetime], end_time: Optional[datetime]) -> None:
    if start_time is None or end_time is None:
        return

    if start_time.tzinfo is None and end_time.tzinfo is not None:
        start_time = start_time.replace(tzinfo=end_time.tzinfo)
    elif end_time.tzinfo is None and start_time.tzinfo is not None:
        end_time = end_time.replace(tzinfo=start_time.tzinfo)

    if end_time < start_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="end_time must be after start_time")


def _assert_no_active_trip_for_booking(db: Session, booking_id: int, organization_id: str) -> None:
    active_trip = trip_repository.get_active_trip_for_booking(db, booking_id, organization_id)
    if active_trip:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="There is already an active trip for this booking")


def _load_package(db: Session, package_id: Optional[int], organization_id: str) -> Optional[TripPackage]:
    if package_id is None:
        return None
    package = package_repository.get_package_by_id(db, package_id, organization_id)
    if not package:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Package not found")
    return package


def _merge_trip_payload(trip: Trip, payload_data: Dict[str, Any]) -> Dict[str, Any]:
    merged = {
        "package_id": trip.package_id,
        "start_place": trip.start_place,
        "end_place": trip.end_place,
        "start_km": trip.start_km,
        "end_km": trip.end_km,
        "start_time": trip.start_time,
        "end_time": trip.end_time,
        "package_amount": trip.package_amount,
        "extra_km_rate": trip.extra_km_rate,
        "extra_hour_rate": trip.extra_hour_rate,
        "minimum_km_per_day": trip.minimum_km_per_day,
        "km_rate": trip.km_rate,
        "driver_bata": trip.driver_bata,
        "night_charges": trip.night_charges,
        "permit_amount": trip.permit_amount,
        "state_tax_amount": trip.state_tax_amount,
        "toll_amount": trip.toll_amount,
        "parking_amount": trip.parking_amount,
    }
    merged.update(payload_data)
    return merged


def can_accept_expenses(trip: Trip) -> bool:
    return trip.status == TripStatusEnum.COMPLETED


def create_trip_service(db: Session, current_user: User, payload: TripCreate) -> Trip:
    organization_id = str(current_user.organization_id)
    booking = _assert_booking_belongs_to_org(db, payload.booking_id, organization_id)
    _assert_vehicle_matches_booking(booking, payload.vehicle_id)
    _assert_no_active_trip_for_booking(db, payload.booking_id, organization_id)
    _validate_distance(payload.start_km, payload.end_km)
    _validate_time_order(payload.start_time, payload.end_time)

    package = _load_package(db, payload.package_id, organization_id)
    trip_values = payload.dict(exclude_none=True)
    computed = calculate_trip_financials(package, trip_values)

    trip = Trip(
        organization_id=current_user.organization_id,
        booking_id=payload.booking_id,
        vehicle_id=payload.vehicle_id,
        package_id=payload.package_id,
        package_name=computed.get("package_name"),
        trip_date=computed.get("trip_date"),
        start_place=payload.start_place,
        end_place=payload.end_place,
        start_km=payload.start_km,
        end_km=payload.end_km,
        distance_km=computed.get("distance_km"),
        included_km=computed.get("included_km"),
        included_hours=computed.get("included_hours"),
        hours_used=computed.get("hours_used"),
        days_used=computed.get("days_used"),
        extra_km=computed.get("extra_km"),
        extra_hours=computed.get("extra_hours"),
        package_amount=computed.get("package_amount"),
        extra_km_rate=payload.extra_km_rate,
        extra_hour_rate=payload.extra_hour_rate,
        minimum_km_per_day=payload.minimum_km_per_day,
        km_rate=payload.km_rate,
        extra_km_amount=computed.get("extra_km_amount"),
        extra_hour_amount=computed.get("extra_hour_amount"),
        driver_bata=computed.get("driver_bata"),
        night_charges=computed.get("night_charges"),
        permit_amount=computed.get("permit_amount"),
        state_tax_amount=computed.get("state_tax_amount"),
        toll_amount=computed.get("toll_amount"),
        parking_amount=computed.get("parking_amount"),
        grand_total=computed.get("grand_total"),
        trip_revenue=computed.get("trip_revenue"),
        start_time=payload.start_time,
        end_time=payload.end_time,
        status=payload.status or TripStatusEnum.PENDING,
        notes=payload.notes,
    )
    trip = trip_repository.create_trip(db, trip)
    _create_audit_log(db, current_user, organization_id, trip.id, "create", payload.dict(exclude_none=True))
    profit_service.recalculate_trip_profit(db, trip.id, organization_id)
    return trip


def get_trip_service(db: Session, trip_id: int, current_user: User) -> Trip:
    organization_id = str(current_user.organization_id)
    trip = trip_repository.get_trip_by_id(db, trip_id, organization_id)
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return trip


def update_trip_service(db: Session, trip_id: int, current_user: User, payload: TripUpdate) -> Trip:
    organization_id = str(current_user.organization_id)
    trip = trip_repository.get_trip_by_id(db, trip_id, organization_id)
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    if trip.status == TripStatusEnum.CANCELLED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot update a cancelled trip")

    payload_data = payload.dict(exclude_none=True)
    if payload_data.get("end_km") is not None:
        start_km = payload_data.get("start_km", trip.start_km)
        _validate_distance(start_km, payload_data["end_km"])

    merged_values = _merge_trip_payload(trip, payload_data)
    package = _load_package(db, merged_values.get("package_id"), organization_id)
    computed = calculate_trip_financials(package, merged_values)

    trip_data = {
        **payload_data,
        "package_name": computed.get("package_name"),
        "trip_date": computed.get("trip_date"),
        "distance_km": computed.get("distance_km"),
        "included_km": computed.get("included_km"),
        "included_hours": computed.get("included_hours"),
        "hours_used": computed.get("hours_used"),
        "days_used": computed.get("days_used"),
        "extra_km": computed.get("extra_km"),
        "extra_hours": computed.get("extra_hours"),
        "package_amount": computed.get("package_amount"),
        "extra_km_rate": merged_values.get("extra_km_rate"),
        "extra_hour_rate": merged_values.get("extra_hour_rate"),
        "minimum_km_per_day": merged_values.get("minimum_km_per_day"),
        "km_rate": merged_values.get("km_rate"),
        "extra_km_amount": computed.get("extra_km_amount"),
        "extra_hour_amount": computed.get("extra_hour_amount"),
        "driver_bata": computed.get("driver_bata"),
        "night_charges": computed.get("night_charges"),
        "permit_amount": computed.get("permit_amount"),
        "state_tax_amount": computed.get("state_tax_amount"),
        "toll_amount": computed.get("toll_amount"),
        "parking_amount": computed.get("parking_amount"),
        "grand_total": computed.get("grand_total"),
        "trip_revenue": computed.get("trip_revenue"),
    }

    trip = trip_repository.update_trip(db, trip, trip_data)
    _create_audit_log(db, current_user, organization_id, trip.id, "update", trip_data)
    profit_service.recalculate_trip_profit(db, trip.id, organization_id)
    return trip


def start_trip_service(db: Session, trip_id: int, current_user: User) -> Trip:
    organization_id = str(current_user.organization_id)
    trip = trip_repository.get_trip_by_id(db, trip_id, organization_id)
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    if trip.status == TripStatusEnum.CANCELLED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cancelled trips cannot be started")
    if trip.status == TripStatusEnum.COMPLETED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Completed trips cannot be started")
    if trip.status == TripStatusEnum.ONGOING:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Trip is already in progress")

    trip_data = {
        "status": TripStatusEnum.ONGOING,
        "start_time": trip.start_time or datetime.utcnow(),
    }
    trip = trip_repository.update_trip(db, trip, trip_data)
    _create_audit_log(db, current_user, organization_id, trip.id, "start", trip_data)
    return trip


def complete_trip_service(db: Session, trip_id: int, current_user: User, payload: TripCompleteRequest) -> Trip:
    organization_id = str(current_user.organization_id)
    trip = trip_repository.get_trip_by_id(db, trip_id, organization_id)
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    if trip.status == TripStatusEnum.CANCELLED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cancelled trips cannot be completed")
    if trip.status == TripStatusEnum.COMPLETED:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Trip is already completed")

    _validate_distance(trip.start_km, payload.end_km)
    end_time = payload.end_time or datetime.utcnow()
    _validate_time_order(trip.start_time, end_time)

    payload_data = {
        "end_km": payload.end_km,
        "end_time": end_time,
        "status": TripStatusEnum.COMPLETED,
    }
    merged_values = _merge_trip_payload(trip, payload_data)
    package = _load_package(db, merged_values.get("package_id"), organization_id)
    computed = calculate_trip_financials(package, merged_values)

    trip_data = {
        **payload_data,
        "distance_km": computed.get("distance_km"),
        "included_km": computed.get("included_km"),
        "included_hours": computed.get("included_hours"),
        "hours_used": computed.get("hours_used"),
        "days_used": computed.get("days_used"),
        "extra_km": computed.get("extra_km"),
        "extra_hours": computed.get("extra_hours"),
        "package_amount": computed.get("package_amount"),
        "extra_km_rate": merged_values.get("extra_km_rate"),
        "extra_hour_rate": merged_values.get("extra_hour_rate"),
        "minimum_km_per_day": merged_values.get("minimum_km_per_day"),
        "km_rate": merged_values.get("km_rate"),
        "extra_km_amount": computed.get("extra_km_amount"),
        "extra_hour_amount": computed.get("extra_hour_amount"),
        "driver_bata": computed.get("driver_bata"),
        "night_charges": computed.get("night_charges"),
        "permit_amount": computed.get("permit_amount"),
        "state_tax_amount": computed.get("state_tax_amount"),
        "toll_amount": computed.get("toll_amount"),
        "parking_amount": computed.get("parking_amount"),
        "grand_total": computed.get("grand_total"),
        "trip_revenue": computed.get("trip_revenue"),
    }
    trip = trip_repository.update_trip(db, trip, trip_data)
    _create_audit_log(db, current_user, organization_id, trip.id, "complete", trip_data)
    profit_service.recalculate_trip_profit(db, trip.id, organization_id)

    invoice_service = InvoiceService(db)
    invoice_payload = InvoiceCreate(trip_id=trip.id)
    invoice_service.create_invoice(organization_id, invoice_payload, current_user.id)

    return trip


def list_trips_service(
    db: Session,
    current_user: User,
    booking_id: Optional[int] = None,
    vehicle_id: Optional[int] = None,
    status: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 25,
) -> Tuple[list[Trip], int]:
    if page < 1 or page_size < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid pagination parameters")

    organization_id = str(current_user.organization_id)
    offset = (page - 1) * page_size
    return trip_repository.list_trips(
        db,
        organization_id=organization_id,
        booking_id=booking_id,
        vehicle_id=vehicle_id,
        status=status,
        start_time=start_time,
        end_time=end_time,
        offset=offset,
        limit=page_size,
    )
