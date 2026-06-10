from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class LoginRequest(BaseModel):
    organization_id: Optional[UUID] = None
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role_names: Optional[List[str]] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("password")
    def password_minimum_length(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return value


class UserResponse(BaseModel):
    id: UUID
    organization_id: Optional[UUID]
    email: EmailStr
    is_active: bool
    is_superuser: bool
    roles: List[str] = []

    @field_validator("roles", mode="before")
    def flatten_roles(cls, value):
        if value is None:
            return []
        if isinstance(value, list):
            return [item.name if hasattr(item, "name") else item for item in value]
        return [value]

    model_config = ConfigDict(from_attributes=True)


class AuthTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

    model_config = ConfigDict(from_attributes=True)
