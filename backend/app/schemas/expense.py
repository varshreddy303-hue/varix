from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

from ..db.models import ExpenseCategoryEnum


class ExpenseBase(BaseModel):
    trip_id: Optional[int] = None
    booking_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    category: Optional[ExpenseCategoryEnum] = ExpenseCategoryEnum.OTHER
    amount: Optional[float] = 0.0
    fuel_amount: Optional[float] = 0.0
    toll_amount: Optional[float] = 0.0
    parking_amount: Optional[float] = 0.0
    driver_bata_amount: Optional[float] = 0.0
    permit_amount: Optional[float] = 0.0
    state_tax_amount: Optional[float] = 0.0
    food_amount: Optional[float] = 0.0
    accommodation_amount: Optional[float] = 0.0
    misc_amount: Optional[float] = 0.0
    total_amount: Optional[float] = 0.0
    description: Optional[str] = None
    expense_date: datetime

    @field_validator("category", mode="before")
    def normalize_category(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return ExpenseCategoryEnum.OTHER
        return str(value).strip().lower()

    @field_validator("amount", "fuel_amount", "toll_amount", "parking_amount", "driver_bata_amount", "permit_amount", "state_tax_amount", "food_amount", "accommodation_amount", "misc_amount", "total_amount")
    def validate_amount(cls, value: Optional[float]) -> Optional[float]:
        if value is None:
            return 0.0
        if value < 0:
            raise ValueError("amount values must be greater than or equal to 0")
        return value

    @field_validator("description")
    def normalize_description(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return value.strip()


class ExpenseCreate(ExpenseBase):
    @field_validator("trip_id", "booking_id", mode="before")
    def normalize_optional_ids(cls, value):
        return value if value not in (None, "") else None

    @field_validator("trip_id")
    def validate_trip_or_booking(cls, value, info):
        data = info.data
        if value is None and data.get("booking_id") is None:
            raise ValueError("Either trip_id or booking_id is required")
        return value


class ExpenseUpdate(BaseModel):
    trip_id: Optional[int] = None
    booking_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    category: Optional[ExpenseCategoryEnum] = None
    amount: Optional[float] = None
    fuel_amount: Optional[float] = None
    toll_amount: Optional[float] = None
    parking_amount: Optional[float] = None
    driver_bata_amount: Optional[float] = None
    permit_amount: Optional[float] = None
    state_tax_amount: Optional[float] = None
    food_amount: Optional[float] = None
    accommodation_amount: Optional[float] = None
    misc_amount: Optional[float] = None
    total_amount: Optional[float] = None
    description: Optional[str] = None
    expense_date: Optional[datetime] = None

    @field_validator("category", mode="before")
    def normalize_category(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return str(value).strip().lower()

    @field_validator("amount")
    def validate_amount(cls, value: Optional[float]) -> Optional[float]:
        if value is None:
            return value
        if value < 0:
            raise ValueError("amount must be greater than or equal to 0")
        return value

    @field_validator("description")
    def normalize_description(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return value.strip()


class ExpenseResponse(ExpenseBase):
    id: int
    organization_id: UUID
    vehicle_id: int
    created_at: datetime
    updated_at: datetime
    category: str

    @field_validator("category", mode="before")
    def serialize_category(cls, value):
        if value is None:
            return value
        if isinstance(value, ExpenseCategoryEnum):
            return value.value
        return str(value)

    model_config = ConfigDict(from_attributes=True)
