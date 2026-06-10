from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from ..db.models import Expense


def get_expense_by_id(db: Session, expense_id: int, organization_id: Optional[str] = None) -> Optional[Expense]:
    query = db.query(Expense).filter(Expense.id == expense_id)
    if organization_id:
        query = query.filter(Expense.organization_id == organization_id)
    return query.first()


def list_expenses(
    db: Session,
    organization_id: Optional[str] = None,
    trip_id: Optional[int] = None,
    vehicle_id: Optional[int] = None,
    category: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    offset: int = 0,
    limit: int = 50,
) -> Tuple[List[Expense], int]:
    query = db.query(Expense)
    if organization_id:
        query = query.filter(Expense.organization_id == organization_id)
    if trip_id is not None:
        query = query.filter(Expense.trip_id == trip_id)
    if vehicle_id is not None:
        query = query.filter(Expense.vehicle_id == vehicle_id)
    if category:
        query = query.filter(Expense.category == category)
    if start_date:
        query = query.filter(Expense.expense_date >= start_date)
    if end_date:
        query = query.filter(Expense.expense_date <= end_date)

    total = query.count()
    expenses = query.order_by(Expense.expense_date.desc()).offset(offset).limit(limit).all()
    return expenses, total


def create_expense(db: Session, expense: Expense) -> Expense:
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


def update_expense(db: Session, expense: Expense, values: dict) -> Expense:
    for key, value in values.items():
        setattr(expense, key, value)
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


def delete_expense(db: Session, expense: Expense) -> None:
    db.delete(expense)
    db.commit()
