from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TripPackageBase(BaseModel):
    name: str = Field(..., min_length=1)
    package_category: str = Field(..., min_length=1)
    included_hours: Optional[int] = Field(None, ge=0)
    included_km: Optional[int] = Field(None, ge=0)
    base_amount: Optional[float] = Field(None, ge=0)
    extra_km_rate: Optional[float] = Field(None, ge=0)
    extra_hour_rate: Optional[float] = Field(None, ge=0)
    driver_bata_default: Optional[float] = Field(None, ge=0)
    night_charge_default: Optional[float] = Field(None, ge=0)
    permit_default: Optional[float] = Field(None, ge=0)
    state_tax_default: Optional[float] = Field(None, ge=0)
    minimum_km_per_day: Optional[int] = Field(None, ge=0)
    km_rate: Optional[float] = Field(None, ge=0)
    active: bool = True

    @field_validator("name", "package_category")
    @classmethod
    def non_empty_strings(cls, value: str) -> str:
        return value.strip()


class TripPackageCreate(TripPackageBase):
    pass


class TripPackageUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    package_category: Optional[str] = Field(None, min_length=1)
    included_hours: Optional[int] = Field(None, ge=0)
    included_km: Optional[int] = Field(None, ge=0)
    base_amount: Optional[float] = Field(None, ge=0)
    extra_km_rate: Optional[float] = Field(None, ge=0)
    extra_hour_rate: Optional[float] = Field(None, ge=0)
    driver_bata_default: Optional[float] = Field(None, ge=0)
    night_charge_default: Optional[float] = Field(None, ge=0)
    permit_default: Optional[float] = Field(None, ge=0)
    state_tax_default: Optional[float] = Field(None, ge=0)
    minimum_km_per_day: Optional[int] = Field(None, ge=0)
    km_rate: Optional[float] = Field(None, ge=0)
    active: Optional[bool] = None

    @field_validator("name", "package_category")
    @classmethod
    def strip_strings(cls, value: Optional[str]) -> Optional[str]:
        return value.strip() if value is not None else value


class TripPackageResponse(TripPackageBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
