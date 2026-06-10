from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..core.dependencies import get_current_user
from ..models import User
from ..schemas.calendar import CalendarEventResponse
from ..services import calendar_service

router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.get("/", response_model=List[CalendarEventResponse])
def get_calendar_events(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return calendar_service.list_calendar_events_service(db, current_user, start_date, end_date)
