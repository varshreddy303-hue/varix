from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, validator


class TripStatusEnum(str):
    PENDING = "pending"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TripBase(BaseModel):
    booking_id: int
    vehicle_id: int
    package_id: Optional[int] = Field(None, ge=1)
    start_place: Optional[str] = Field(None, min_length=1, max_length=500)
    end_place: Optional[str] = Field(None, min_length=1, max_length=500)
    start_km: int = Field(..., ge=0)
    end_km: Optional[int] = Field(None, ge=0)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    package_amount: Optional[float] = Field(None, ge=0)
    extra_km_rate: Optional[float] = Field(None, ge=0)
    extra_hour_rate: Optional[float] = Field(None, ge=0)
    minimum_km_per_day: Optional[int] = Field(None, ge=0)
    km_rate: Optional[float] = Field(None, ge=0)
    driver_bata: Optional[float] = Field(None, ge=0)
    night_charges: Optional[float] = Field(None, ge=0)
    permit_amount: Optional[float] = Field(None, ge=0)
    state_tax_amount: Optional[float] = Field(None, ge=0)
    toll_amount: Optional[float] = Field(None, ge=0)
    parking_amount: Optional[float] = Field(None, ge=0)
    advance_received: Optional[float] = Field(None, ge=0)
    grand_total: Optional[float] = Field(None, ge=0)
    trip_revenue: Optional[float] = Field(None, ge=0)
    status: Optional[str] = Field(None, description="Trip status")
    notes: Optional[str] = None

    @validator("end_km")
    def validate_end_km(cls, value):
        return value


class TripCreate(TripBase):
    status: Optional[str] = Field(default=TripStatusEnum.PENDING)


class TripUpdate(BaseModel):
    package_id: Optional[int] = Field(None, ge=1)
    start_place: Optional[str] = Field(None, min_length=1, max_length=500)
    end_place: Optional[str] = Field(None, min_length=1, max_length=500)
    start_km: Optional[int] = Field(None, ge=0)
    end_km: Optional[int] = Field(None, ge=0)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    package_amount: Optional[float] = Field(None, ge=0)
    extra_km_rate: Optional[float] = Field(None, ge=0)
    extra_hour_rate: Optional[float] = Field(None, ge=0)
    minimum_km_per_day: Optional[int] = Field(None, ge=0)
    km_rate: Optional[float] = Field(None, ge=0)
    driver_bata: Optional[float] = Field(None, ge=0)
    night_charges: Optional[float] = Field(None, ge=0)
    permit_amount: Optional[float] = Field(None, ge=0)
    state_tax_amount: Optional[float] = Field(None, ge=0)
    toll_amount: Optional[float] = Field(None, ge=0)
    parking_amount: Optional[float] = Field(None, ge=0)
    advance_received: Optional[float] = Field(None, ge=0)
    grand_total: Optional[float] = Field(None, ge=0)
    trip_revenue: Optional[float] = Field(None, ge=0)
    status: Optional[str] = Field(None, description="Trip status")
    notes: Optional[str] = None

    @validator("end_km")
    def validate_end_km(cls, value):
        if value is not None and value < 0:
            raise ValueError("end_km must be greater than or equal to 0")
        return value


class TripCompleteRequest(BaseModel):
    end_km: int = Field(..., ge=0)
    end_time: Optional[datetime] = None


class TripResponse(BaseModel):
    id: int
    booking_id: int
    vehicle_id: int
    package_id: Optional[int] = None
    package_name: Optional[str] = None
    trip_date: Optional[date] = None
    start_place: Optional[str] = None
    end_place: Optional[str] = None
    start_km: int
    end_km: Optional[int] = None
    distance_km: Optional[float] = None
    included_km: Optional[int] = None
    included_hours: Optional[int] = None
    hours_used: Optional[float] = None
    days_used: Optional[int] = None
    extra_km: Optional[float] = None
    extra_hours: Optional[float] = None
    package_amount: Optional[float] = None
    extra_km_amount: Optional[float] = None
    extra_hour_amount: Optional[float] = None
    driver_bata: Optional[float] = None
    night_charges: Optional[float] = None
    permit_amount: Optional[float] = None
    state_tax_amount: Optional[float] = None
    toll_amount: Optional[float] = None
    parking_amount: Optional[float] = None
    advance_received: Optional[float] = None
    grand_total: Optional[float] = None
    trip_revenue: Optional[float] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
