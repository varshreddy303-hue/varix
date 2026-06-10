from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from ..core.dependencies import get_current_user, require_roles
from ..database import get_db
from ..models import User
from ..schemas.trip import (
    TripCompleteRequest,
    TripCreate,
    TripResponse,
    TripUpdate,
)
from ..services import trip_service

router = APIRouter(prefix="/trips", tags=["trips"])


@router.post("/", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
def create_trip(
    payload: TripCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    return trip_service.create_trip_service(db, current_user, payload)


@router.get("/", response_model=List[TripResponse])
def list_trips(
    db: Session = Depends(get_db),
    booking_id: Optional[int] = Query(None, description="Filter by booking id"),
    vehicle_id: Optional[int] = Query(None, description="Filter by vehicle id"),
    status: Optional[str] = Query(None, description="Filter by trip status"),
    start_time: Optional[datetime] = Query(None, description="Filter trips started on or after this time"),
    end_time: Optional[datetime] = Query(None, description="Filter trips ended on or or before this time"),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
    current_user: User = Depends(get_current_user),
):
    items, _ = trip_service.list_trips_service(
        db,
        current_user,
        booking_id=booking_id,
        vehicle_id=vehicle_id,
        status=status,
        start_time=start_time,
        end_time=end_time,
        page=page,
        page_size=page_size,
    )
    return items


@router.get("/{trip_id}", response_model=TripResponse)
def get_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return trip_service.get_trip_service(db, trip_id, current_user)


@router.put("/{trip_id}", response_model=TripResponse)
def update_trip(
    trip_id: int,
    payload: TripUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    return trip_service.update_trip_service(db, trip_id, current_user, payload)


@router.post("/{trip_id}/start", response_model=TripResponse)
def start_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    return trip_service.start_trip_service(db, trip_id, current_user)


@router.post("/{trip_id}/complete", response_model=TripResponse)
def complete_trip(
    trip_id: int,
    payload: TripCompleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    return trip_service.complete_trip_service(db, trip_id, current_user, payload)
