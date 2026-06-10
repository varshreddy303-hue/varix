from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from ..core.dependencies import get_current_user, require_roles
from ..database import get_db
from ..models import User
from ..schemas.profit import (
    TripProfitResponse,
    VehicleDailyProfitResponse,
    VehicleMonthlyProfitResponse,
    ProfitSummaryResponse,
)
from ..services import profit_service

router = APIRouter(prefix="/profits", tags=["profits"])


@router.get("/trip/{trip_id}", response_model=TripProfitResponse)
def get_trip_profit(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return profit_service.get_trip_profit_service(db, trip_id, current_user)


@router.get("/vehicle/{vehicle_id}/daily", response_model=List[VehicleDailyProfitResponse])
def list_vehicle_daily_profit(
    vehicle_id: int,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
    current_user: User = Depends(get_current_user),
):
    items, _ = profit_service.list_vehicle_daily_profit_service(
        db,
        vehicle_id,
        current_user,
        page=page,
        page_size=page_size,
    )
    return items


@router.get("/vehicle/{vehicle_id}/monthly", response_model=List[VehicleMonthlyProfitResponse])
def list_vehicle_monthly_profit(
    vehicle_id: int,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
    current_user: User = Depends(get_current_user),
):
    items, _ = profit_service.list_vehicle_monthly_profit_service(
        db,
        vehicle_id,
        current_user,
        page=page,
        page_size=page_size,
    )
    return items


@router.get("/summary", response_model=ProfitSummaryResponse)
def get_profit_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return profit_service.get_profit_summary_service(db, current_user)
