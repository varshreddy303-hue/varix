from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..db.models import AuditLog, Expense, ExpenseCategoryEnum, Trip, TripStatusEnum, User
from ..repositories import booking_repository, expense_repository, trip_repository
from ..schemas.expense import ExpenseCreate, ExpenseUpdate
from . import profit_service
from .audit_utils import serialize_audit_changes


def _create_audit_log(db: Session, user: User, organization_id: str, entity_id: int, action: str, changes: dict) -> AuditLog:
    audit = AuditLog(
        organization_id=organization_id,
        user_id=user.id,
        entity_type="expense",
        entity_id=entity_id,
        action=action,
        changes=serialize_audit_changes(changes),
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit


def _assert_trip_eligible_for_expense(trip: Optional[Trip]) -> Trip:
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    if trip.status == TripStatusEnum.CANCELLED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot add expense to a cancelled trip")
    return trip


def _sum_expense_components(payload: ExpenseCreate | ExpenseUpdate) -> float:
    components = [
        payload.fuel_amount,
        payload.toll_amount,
        payload.parking_amount,
        payload.driver_bata_amount,
        payload.permit_amount,
        payload.state_tax_amount,
        payload.food_amount,
        payload.accommodation_amount,
        payload.misc_amount,
    ]
    return sum(float(value or 0.0) for value in components)


def create_expense_service(db: Session, current_user: User, payload: ExpenseCreate) -> Expense:
    organization_id = str(current_user.organization_id)

    trip: Optional[Trip] = None
    vehicle_id = payload.vehicle_id

    if payload.trip_id is not None:
        trip = trip_repository.get_trip_by_id(db, payload.trip_id, organization_id)
        trip = _assert_trip_eligible_for_expense(trip)
        vehicle_id = trip.vehicle_id if vehicle_id is None else vehicle_id
    elif payload.booking_id is not None:
        booking = booking_repository.get_booking_by_id(db, payload.booking_id, organization_id)
        if not booking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
        vehicle_id = booking.vehicle_id if vehicle_id is None else vehicle_id
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Either trip_id or booking_id is required")

    total_amount = _sum_expense_components(payload)
    amount = float(payload.amount or 0.0) if payload.amount is not None else total_amount
    if total_amount > 0.0:
        amount = max(amount, total_amount)

    expense = Expense(
        organization_id=current_user.organization_id,
        trip_id=payload.trip_id,
        booking_id=payload.booking_id,
        vehicle_id=vehicle_id,
        category=payload.category or ExpenseCategoryEnum.OTHER,
        amount=amount,
        fuel_amount=payload.fuel_amount,
        toll_amount=payload.toll_amount,
        parking_amount=payload.parking_amount,
        driver_bata_amount=payload.driver_bata_amount,
        permit_amount=payload.permit_amount,
        state_tax_amount=payload.state_tax_amount,
        food_amount=payload.food_amount,
        accommodation_amount=payload.accommodation_amount,
        misc_amount=payload.misc_amount,
        total_amount=total_amount,
        description=payload.description,
        expense_date=payload.expense_date,
    )
    expense = expense_repository.create_expense(db, expense)
    _create_audit_log(db, current_user, organization_id, expense.id, "create", payload.dict(exclude_none=True))
    if trip is not None and trip.id is not None:
        profit_service.recalculate_trip_profit(db, trip.id, organization_id)
    return expense


def get_expense_service(db: Session, expense_id: int, current_user: User) -> Expense:
    organization_id = str(current_user.organization_id)
    expense = expense_repository.get_expense_by_id(db, expense_id, organization_id)
    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    return expense


def update_expense_service(db: Session, expense_id: int, current_user: User, payload: ExpenseUpdate) -> Expense:
    organization_id = str(current_user.organization_id)
    expense = expense_repository.get_expense_by_id(db, expense_id, organization_id)
    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")

    update_data: Dict[str, Any] = {k: v for k, v in payload.dict().items() if v is not None}

    previous_trip_id = expense.trip_id
    if "trip_id" in update_data and update_data["trip_id"] is not None:
        trip = trip_repository.get_trip_by_id(db, update_data["trip_id"], organization_id)
        trip = _assert_trip_eligible_for_expense(trip)
        update_data["vehicle_id"] = trip.vehicle_id
    elif "booking_id" in update_data and update_data["booking_id"] is not None:
        booking = booking_repository.get_booking_by_id(db, update_data["booking_id"], organization_id)
        if not booking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
        update_data["vehicle_id"] = booking.vehicle_id

    if any(key in update_data for key in [
        "fuel_amount",
        "toll_amount",
        "parking_amount",
        "driver_bata_amount",
        "permit_amount",
        "state_tax_amount",
        "food_amount",
        "accommodation_amount",
        "misc_amount",
    ]):
        total_amount = sum(float(update_data.get(field, getattr(expense, field) or 0.0)) for field in [
            "fuel_amount",
            "toll_amount",
            "parking_amount",
            "driver_bata_amount",
            "permit_amount",
            "state_tax_amount",
            "food_amount",
            "accommodation_amount",
            "misc_amount",
        ])
        update_data["total_amount"] = total_amount
        if "amount" not in update_data:
            update_data["amount"] = max(float(expense.amount or 0.0), total_amount)

    expense = expense_repository.update_expense(db, expense, update_data)
    _create_audit_log(db, current_user, organization_id, expense.id, "update", update_data)
    profit_service.recalculate_trip_profit(db, expense.trip_id, organization_id)
    if update_data.get("trip_id") and previous_trip_id != expense.trip_id:
        profit_service.recalculate_trip_profit(db, previous_trip_id, organization_id)
    return expense


def delete_expense_service(db: Session, expense_id: int, current_user: User) -> None:
    organization_id = str(current_user.organization_id)
    expense = expense_repository.get_expense_by_id(db, expense_id, organization_id)
    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")

    trip_id = expense.trip_id
    expense_repository.delete_expense(db, expense)
    _create_audit_log(db, current_user, organization_id, expense.id, "delete", {})
    profit_service.recalculate_trip_profit(db, trip_id, organization_id)


def list_expenses_service(
    db: Session,
    current_user: User,
    trip_id: Optional[int] = None,
    vehicle_id: Optional[int] = None,
    category: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 25,
) -> Tuple[list[Expense], int]:
    if page < 1 or page_size < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid pagination parameters")

    organization_id = str(current_user.organization_id)
    offset = (page - 1) * page_size
    return expense_repository.list_expenses(
        db,
        organization_id=organization_id,
        trip_id=trip_id,
        vehicle_id=vehicle_id,
        category=category,
        start_date=start_date,
        end_date=end_date,
        offset=offset,
        limit=page_size,
    )
