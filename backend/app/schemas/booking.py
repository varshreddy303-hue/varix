from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class BookingBase(BaseModel):
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None
    customer_company: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    customer_gst_number: Optional[str] = None
    customer_city: Optional[str] = None
    customer_notes: Optional[str] = None
    vehicle_id: int
    pickup_location: str
    destination: str
    start_date: datetime
    end_date: datetime
    booking_amount: float
    status: Optional[str] = None

    @field_validator("pickup_location", "destination")
    def trim_text_fields(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Location fields must not be empty")
        return value.strip()

    @field_validator("end_date")
    def validate_date_range(cls, value: datetime, info):
        start_date = info.data.get("start_date")
        if start_date and value <= start_date:
            raise ValueError("end_date must be after start_date")
        return value


class BookingCreate(BookingBase):
    status: Optional[str] = "pending"

    @model_validator(mode="after")
    def ensure_customer_reference_or_contact(self):
        if self.customer_id is not None:
            return self

        has_contact = any(
            field and str(field).strip()
            for field in (self.customer_name, self.customer_phone, self.customer_company)
        )
        if has_contact:
            return self

        raise ValueError("Provide customer_id or at least a customer name/phone for booking-first reservations")


class BookingUpdate(BaseModel):
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None
    customer_company: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    customer_gst_number: Optional[str] = None
    customer_city: Optional[str] = None
    customer_notes: Optional[str] = None
    vehicle_id: Optional[int] = None
    pickup_location: Optional[str] = None
    destination: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    booking_amount: Optional[float] = None
    status: Optional[str] = None

    @field_validator("pickup_location", "destination")
    def trim_text_fields(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if not value.strip():
            raise ValueError("Location fields must not be empty")
        return value.strip()

    @field_validator("end_date")
    def validate_date_range(cls, value: Optional[datetime], info):
        if value is None:
            return value
        start_date = info.data.get("start_date")
        if start_date and value <= start_date:
            raise ValueError("end_date must be after start_date")
        return value


class BookingResponse(BookingBase):
    id: int
    organization_id: UUID
    status: str
    driver_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BookingAvailabilityResponse(BaseModel):
    vehicle_id: int
    start_date: datetime
    end_date: datetime
    available: bool

    model_config = ConfigDict(from_attributes=True)
