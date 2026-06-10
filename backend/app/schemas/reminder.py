from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ReminderRuleBase(BaseModel):
    name: str
    category: str
    event_type: str
    description: Optional[str] = None
    active: Optional[bool] = True
    trigger_days_before: Optional[int] = None
    threshold_hours: Optional[int] = None
    priority: Optional[int] = 100
    settings: Optional[dict] = None

    @field_validator("trigger_days_before", "threshold_hours", "priority")
    def validate_non_negative(cls, value: Optional[int]) -> Optional[int]:
        if value is None:
            return value
        if value < 0:
            raise ValueError("Value must be non-negative")
        return value


class ReminderRuleCreate(ReminderRuleBase):
    pass


class ReminderRuleUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    event_type: Optional[str] = None
    description: Optional[str] = None
    active: Optional[bool] = None
    trigger_days_before: Optional[int] = None
    threshold_hours: Optional[int] = None
    priority: Optional[int] = None
    settings: Optional[dict] = None

    @field_validator("trigger_days_before", "threshold_hours", "priority")
    def validate_non_negative(cls, value: Optional[int]) -> Optional[int]:
        if value is None:
            return value
        if value < 0:
            raise ValueError("Value must be non-negative")
        return value


class ReminderRuleResponse(ReminderRuleBase):
    id: int
    organization_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReminderResponse(BaseModel):
    id: int
    rule_id: int
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    reminder_date: datetime
    due_date: Optional[datetime] = None
    status: str
    message: Optional[str] = None
    payload: Optional[dict] = None
    organization_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationPreferenceBase(BaseModel):
    event_type: str
    channel: str
    enabled: bool = True
    metadata: Optional[dict] = Field(default=None, alias='metadata_json')

    model_config = ConfigDict(populate_by_name=True)


class NotificationPreferenceCreate(NotificationPreferenceBase):
    user_id: Optional[UUID] = None


class NotificationPreferenceResponse(NotificationPreferenceCreate):
    id: int
    organization_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class NotificationEventResponse(BaseModel):
    id: int
    reminder_id: Optional[int] = None
    event_type: str
    recipient_id: Optional[UUID] = None
    channel: str
    status: str
    scheduled_time: Optional[datetime] = None
    payload: Optional[dict] = None
    organization_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
