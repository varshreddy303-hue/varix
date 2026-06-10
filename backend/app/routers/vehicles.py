from datetime import datetime
from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional
from sqlalchemy.orm import Session

from ..database import get_db
from ..core.dependencies import get_current_user, require_roles
from ..models import User
from ..schemas.vehicle import (
    VehicleCreate,
    VehicleResponse,
    VehicleUpdate,
    VehicleUpcomingEMIResponse,
    VehicleAvailabilityResponse,
)
from ..services import vehicle_service

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.post("/", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    payload: VehicleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    return vehicle_service.create_vehicle_service(db, current_user, payload)


@router.get("/", response_model=List[VehicleResponse])
def list_vehicles(
    db: Session = Depends(get_db),
    vehicle_number: Optional[str] = Query(None, description="Search by vehicle number"),
    vehicle_type: Optional[str] = Query(None, description="Search by vehicle type"),
    make: Optional[str] = Query(None, description="Search by make"),
    model: Optional[str] = Query(None, description="Search by model"),
    fuel_type: Optional[str] = Query(None, description="Search by fuel type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
    current_user: User = Depends(get_current_user),
):
    items, _ = vehicle_service.list_vehicles_service(
        db,
        current_user,
        vehicle_number,
        vehicle_type,
        make,
        model,
        fuel_type,
        is_active,
        page,
        page_size,
    )
    return items


@router.get("/expiring-documents", response_model=List[VehicleResponse])
def list_expiring_documents(
    db: Session = Depends(get_db),
    within_days: int = Query(30, ge=1, description="Days window for expiring documents"),
    current_user: User = Depends(get_current_user),
):
    return vehicle_service.list_expiring_documents_service(db, current_user, within_days)


@router.get("/availability", response_model=VehicleAvailabilityResponse)
def check_vehicle_availability(
    db: Session = Depends(get_db),
    vehicle_id: int = Query(..., description="Vehicle id to check availability for"),
    start_date: datetime = Query(..., description="Availability window start date"),
    end_date: datetime = Query(..., description="Availability window end date"),
    current_user: User = Depends(get_current_user),
):
    available, reason = vehicle_service.check_vehicle_availability_service(db, current_user, vehicle_id, start_date, end_date)
    return VehicleAvailabilityResponse(
        vehicle_id=vehicle_id,
        start_date=start_date,
        end_date=end_date,
        available=available,
        reason=reason,
    )


@router.get("/upcoming-emi", response_model=List[VehicleUpcomingEMIResponse])
def list_upcoming_emi(
    db: Session = Depends(get_db),
    within_days: int = Query(30, ge=1, description="Days window for upcoming EMI due dates"),
    current_user: User = Depends(get_current_user),
):
    return vehicle_service.list_upcoming_emi_service(db, current_user, within_days)


@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return vehicle_service.get_vehicle_service(db, vehicle_id, current_user)


@router.put("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
    vehicle_id: int,
    payload: VehicleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    return vehicle_service.update_vehicle_service(db, vehicle_id, current_user, payload)


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    vehicle_service.delete_vehicle_service(db, vehicle_id, current_user)
    return None
