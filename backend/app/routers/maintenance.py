from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..core.dependencies import get_current_user, require_roles
from ..models import User
from ..schemas.maintenance import (
    MaintenanceScheduleCreate,
    MaintenanceScheduleResponse,
    MaintenanceScheduleUpdate,
)
from ..services import maintenance_service

router = APIRouter(prefix="/maintenance", tags=["maintenance"])


@router.post("/", response_model=MaintenanceScheduleResponse, status_code=status.HTTP_201_CREATED)
def create_maintenance_schedule(
    payload: MaintenanceScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    return maintenance_service.create_maintenance_schedule_service(db, current_user, payload)


@router.get("/", response_model=List[MaintenanceScheduleResponse])
def list_maintenance_schedules(
    db: Session = Depends(get_db),
    vehicle_id: Optional[int] = Query(None, description="Filter by vehicle id"),
    start_date: Optional[datetime] = Query(None, description="Filter schedules starting on or after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter schedules ending on or before this date"),
    current_user: User = Depends(get_current_user),
):
    return maintenance_service.list_maintenance_schedules_service(db, current_user, vehicle_id, start_date, end_date)


@router.put("/{maintenance_id}", response_model=MaintenanceScheduleResponse)
def update_maintenance_schedule(
    maintenance_id: int,
    payload: MaintenanceScheduleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    return maintenance_service.update_maintenance_schedule_service(db, maintenance_id, current_user, payload)
