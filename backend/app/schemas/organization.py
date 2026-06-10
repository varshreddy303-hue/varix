from __future__ import annotations

from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class OrganizationRegistrationRequest(BaseModel):
    name: str
    admin_email: EmailStr
    admin_password: str

    model_config = ConfigDict(from_attributes=True)

    @field_validator("admin_password")
    def password_minimum_length(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Admin password must be at least 8 characters long")
        return value


class OrganizationResponse(BaseModel):
    id: UUID
    name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
