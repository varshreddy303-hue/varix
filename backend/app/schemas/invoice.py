from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class InvoiceStatusEnum(str):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"


class InvoiceBase(BaseModel):
    trip_id: Optional[int] = None
    booking_id: Optional[int] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    subtotal: Optional[float] = None
    tax_amount: Optional[float] = 0.0
    advance_received: Optional[float] = 0.0
    notes: Optional[str] = None

    @field_validator("invoice_number")
    def normalize_invoice_number(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        normalized = value.strip()
        if not normalized:
            raise ValueError("invoice_number must not be empty")
        return normalized

    @field_validator("subtotal", "tax_amount", "advance_received")
    def validate_amounts(cls, value: Optional[float]) -> Optional[float]:
        if value is None:
            return value
        if value < 0:
            raise ValueError("amount values must be greater than or equal to 0")
        return value

    @field_validator("notes")
    def normalize_notes(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return value.strip()


class InvoiceCreate(InvoiceBase):
    @model_validator(mode='after')
    def validate_reference(self):
        if self.trip_id is None and self.booking_id is None:
            raise ValueError('Provide trip_id or booking_id to create an invoice')
        return self


class InvoiceUpdate(BaseModel):
    invoice_number: Optional[str] = None
    invoice_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    subtotal: Optional[float] = None
    tax_amount: Optional[float] = None
    advance_received: Optional[float] = None
    notes: Optional[str] = None

    @field_validator("invoice_number")
    def normalize_invoice_number(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        normalized = value.strip()
        if not normalized:
            raise ValueError("invoice_number must not be empty")
        return normalized

    @field_validator("subtotal", "tax_amount", "advance_received")
    def validate_amounts(cls, value: Optional[float]) -> Optional[float]:
        if value is None:
            return value
        if value < 0:
            raise ValueError("amount values must be greater than or equal to 0")
        return value

    @field_validator("notes")
    def normalize_notes(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return value.strip()


class InvoiceItemResponse(BaseModel):
    id: int
    description: Optional[str] = None
    quantity: int
    unit_price_cents: int
    line_total_cents: int

    model_config = ConfigDict(from_attributes=True)


class InvoiceResponse(InvoiceBase):
    id: int
    organization_id: UUID
    customer_id: Optional[int] = None
    total_amount: float
    advance_received: Optional[float] = 0.0
    balance_amount: Optional[float] = 0.0
    status: str
    invoice_items: list[InvoiceItemResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
