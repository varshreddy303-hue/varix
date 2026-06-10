from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CalendarEventType(str, Enum):
    booking = 'booking'
    maintenance = 'maintenance'
    dispatch = 'dispatch'


class CalendarEventResponse(BaseModel):
    id: int
    vehicle_id: int
    title: str
    event_type: CalendarEventType
    status: str
    start_date: datetime
    end_date: datetime
    booking_id: Optional[int] = None
    maintenance_id: Optional[int] = None
    organization_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
