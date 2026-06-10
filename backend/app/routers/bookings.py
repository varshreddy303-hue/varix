from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from ..database import get_db
from ..core.dependencies import get_current_user, require_roles
from ..models import User
from ..schemas.booking import (
    BookingAvailabilityResponse,
    BookingCreate,
    BookingResponse,
    BookingUpdate,
)
from ..services import booking_service

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    payload: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    return booking_service.create_booking_service(db, current_user, payload)


@router.get("/", response_model=List[BookingResponse])
def list_bookings(
    db: Session = Depends(get_db),
    customer_id: Optional[int] = Query(None, description="Filter by customer id"),
    vehicle_id: Optional[int] = Query(None, description="Filter by vehicle id"),
    status: Optional[str] = Query(None, description="Filter by booking status"),
    pickup_location: Optional[str] = Query(None, description="Search by pickup location"),
    destination: Optional[str] = Query(None, description="Search by destination"),
    start_date: Optional[datetime] = Query(None, description="Filter bookings starting on or after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter bookings ending on or before this date"),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
    current_user: User = Depends(get_current_user),
):
    items, _ = booking_service.list_bookings_service(
        db,
        current_user,
        customer_id,
        vehicle_id,
        status,
        pickup_location,
        destination,
        start_date,
        end_date,
        page,
        page_size,
    )
    return items


@router.get("/availability", response_model=BookingAvailabilityResponse)
def check_availability(
    db: Session = Depends(get_db),
    vehicle_id: int = Query(..., description="Vehicle id to check availability for"),
    start_date: datetime = Query(..., description="Booking start date"),
    end_date: datetime = Query(..., description="Booking end date"),
    current_user: User = Depends(get_current_user),
):
    available = booking_service.check_vehicle_availability_service(db, current_user, vehicle_id, start_date, end_date)
    return BookingAvailabilityResponse(
        vehicle_id=vehicle_id,
        start_date=start_date,
        end_date=end_date,
        available=available,
    )


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return booking_service.get_booking_service(db, booking_id, current_user)


@router.put("/{booking_id}", response_model=BookingResponse)
def update_booking(
    booking_id: int,
    payload: BookingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    return booking_service.update_booking_service(db, booking_id, current_user, payload)


@router.post("/{booking_id}/cancel", response_model=BookingResponse)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    return booking_service.cancel_booking_service(db, booking_id, current_user)
