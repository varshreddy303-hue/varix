from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator


class MaintenanceScheduleBase(BaseModel):
    vehicle_id: int
    start_date: datetime
    end_date: datetime
    reason: str
    status: Optional[str] = 'scheduled'

    @field_validator('reason')
    def trim_reason(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError('Reason must not be empty')
        return value.strip()

    @field_validator('end_date')
    def validate_date_range(cls, value: datetime, info):
        start_date = info.data.get('start_date')
        if start_date and value <= start_date:
            raise ValueError('end_date must be after start_date')
        return value


class MaintenanceScheduleCreate(MaintenanceScheduleBase):
    pass


class MaintenanceScheduleUpdate(BaseModel):
    vehicle_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    reason: Optional[str] = None
    status: Optional[str] = None

    @field_validator('reason')
    def trim_reason(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if not value.strip():
            raise ValueError('Reason must not be empty')
        return value.strip()

    @field_validator('end_date')
    def validate_date_range(cls, value: Optional[datetime], info):
        if value is None:
            return value
        start_date = info.data.get('start_date')
        if start_date and value <= start_date:
            raise ValueError('end_date must be after start_date')
        return value


class MaintenanceScheduleResponse(MaintenanceScheduleBase):
    id: int
    organization_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
