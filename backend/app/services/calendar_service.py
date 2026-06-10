from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from ..models import User, VehicleCalendarEvent
from ..repositories import maintenance_repository


def list_calendar_events_service(
    db: Session,
    current_user: User,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> List[VehicleCalendarEvent]:
    organization_id = str(current_user.organization_id)
    return maintenance_repository.list_calendar_events(
        db,
        organization_id=organization_id,
        start_date=start_date,
        end_date=end_date,
    )
