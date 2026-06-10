from datetime import datetime
from typing import Optional
from uuid import UUID
import re

from pydantic import BaseModel, EmailStr, field_validator, model_validator


class CustomerBase(BaseModel):
    customer_name: Optional[str] = None
    company: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    gst_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = True

    @field_validator('customer_name', mode='before')
    def normalize_customer_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        normalized = str(value).strip()
        return normalized or None

    @field_validator('phone_number', mode='before')
    def normalize_phone_number(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        normalized = str(value).strip()
        return normalized or None

    @field_validator('phone_number')
    def phone_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not re.fullmatch(r'^\+?\d{7,15}$', v):
            raise ValueError('Invalid phone number format')
        return v

    @field_validator('gst_number', mode='before')
    def normalize_gst_number(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        normalized = str(value).strip().upper()
        return normalized or None

    @field_validator('gst_number')
    def gst_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not re.fullmatch(r'^[0-9A-Z]{15}$', v):
            raise ValueError('Invalid GST number format')
        return v


class CustomerCreate(CustomerBase):
    @model_validator(mode='after')
    def require_name_or_phone(self):
        if not self.customer_name and not self.phone_number:
            raise ValueError('customer_name or phone_number is required')
        return self


class CustomerUpdate(BaseModel):
    customer_name: Optional[str] = None
    company: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    gst_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator('customer_name', mode='before')
    def normalize_customer_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        normalized = str(value).strip()
        return normalized or None

    @field_validator('phone_number', mode='before')
    def normalize_phone_number(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        normalized = str(value).strip()
        return normalized or None

    @field_validator('phone_number')
    def phone_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not re.fullmatch(r'^\+?\d{7,15}$', v):
            raise ValueError('Invalid phone number format')
        return v

    @field_validator('gst_number', mode='before')
    def normalize_gst_number(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        normalized = str(value).strip().upper()
        return normalized or None

    @field_validator('gst_number')
    def gst_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not re.fullmatch(r'^[0-9A-Z]{15}$', v):
            raise ValueError('Invalid GST number format')
        return v


class CustomerResponse(BaseModel):
    id: int
    organization_id: UUID
    customer_name: str
    company: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    gst_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = True
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }
