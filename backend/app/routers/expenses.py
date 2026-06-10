from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from ..core.dependencies import get_current_user, require_roles
from ..database import get_db
from ..models import User
from ..schemas.expense import ExpenseCreate, ExpenseResponse, ExpenseUpdate
from ..services import expense_service

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    payload: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    return expense_service.create_expense_service(db, current_user, payload)


@router.get("/", response_model=List[ExpenseResponse])
def list_expenses(
    db: Session = Depends(get_db),
    trip_id: Optional[int] = Query(None, description="Filter by trip id"),
    vehicle_id: Optional[int] = Query(None, description="Filter by vehicle id"),
    category: Optional[str] = Query(None, description="Filter by expense category"),
    start_date: Optional[datetime] = Query(None, description="Filter expenses on or after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter expenses on or before this date"),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
    current_user: User = Depends(get_current_user),
):
    items, _ = expense_service.list_expenses_service(
        db,
        current_user,
        trip_id=trip_id,
        vehicle_id=vehicle_id,
        category=category,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
    )
    return items


@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return expense_service.get_expense_service(db, expense_id, current_user)


@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: int,
    payload: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    return expense_service.update_expense_service(db, expense_id, current_user, payload)


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    expense_service.delete_expense_service(db, expense_id, current_user)
    return None
