from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator


class VehicleBase(BaseModel):
    vehicle_number: str
    vehicle_type: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    seating_capacity: Optional[int] = None
    fuel_type: Optional[str] = None
    registration_date: Optional[datetime] = None

    insurance_expiry_date: Optional[datetime] = None
    permit_expiry_date: Optional[datetime] = None
    fc_expiry_date: Optional[datetime] = None
    pollution_expiry_date: Optional[datetime] = None
    road_tax_expiry_date: Optional[datetime] = None
    gps_subscription_expiry_date: Optional[datetime] = None
    service_due_date: Optional[datetime] = None
    tyre_change_due_date: Optional[datetime] = None
    battery_change_due_date: Optional[datetime] = None
    loan_closure_date: Optional[datetime] = None

    purchase_price: Optional[float] = None
    emi_amount: Optional[float] = None
    emi_due_day: Optional[int] = None

    is_active: Optional[bool] = True

    @field_validator("vehicle_number")
    def validate_vehicle_number(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Vehicle number must not be empty")
        return value.strip()

    @field_validator("emi_due_day")
    def validate_emi_due_day(cls, value: Optional[int]) -> Optional[int]:
        if value is None:
            return value
        if value < 1 or value > 31:
            raise ValueError("EMI due day must be between 1 and 31")
        return value


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(BaseModel):
    vehicle_number: Optional[str] = None
    vehicle_type: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    seating_capacity: Optional[int] = None
    fuel_type: Optional[str] = None
    registration_date: Optional[datetime] = None

    insurance_expiry_date: Optional[datetime] = None
    permit_expiry_date: Optional[datetime] = None
    fc_expiry_date: Optional[datetime] = None
    pollution_expiry_date: Optional[datetime] = None
    road_tax_expiry_date: Optional[datetime] = None
    gps_subscription_expiry_date: Optional[datetime] = None
    service_due_date: Optional[datetime] = None
    tyre_change_due_date: Optional[datetime] = None
    battery_change_due_date: Optional[datetime] = None
    loan_closure_date: Optional[datetime] = None

    purchase_price: Optional[float] = None
    emi_amount: Optional[float] = None
    emi_due_day: Optional[int] = None

    is_active: Optional[bool] = None

    @field_validator("vehicle_number")
    def validate_vehicle_number(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if not value.strip():
            raise ValueError("Vehicle number must not be empty")
        return value.strip()

    @field_validator("emi_due_day")
    def validate_emi_due_day(cls, value: Optional[int]) -> Optional[int]:
        if value is None:
            return value
        if value < 1 or value > 31:
            raise ValueError("EMI due day must be between 1 and 31")
        return value


class VehicleResponse(VehicleBase):
    id: int
    organization_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VehicleUpcomingEMIResponse(VehicleResponse):
    next_emi_due_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class VehicleAvailabilityResponse(BaseModel):
    vehicle_id: int
    start_date: datetime
    end_date: datetime
    available: bool
    reason: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
