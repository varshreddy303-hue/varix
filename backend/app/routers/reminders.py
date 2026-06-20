from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..core.dependencies import get_current_user, require_roles
from ..database import get_db
from ..models import User
from ..schemas.reminder import (
    NotificationEventResponse,
    NotificationPreferenceCreate,
    NotificationPreferenceResponse,
    ReminderResponse,
    ReminderRuleCreate,
    ReminderRuleResponse,
    ReminderRuleUpdate,
)
from ..services.reminder_service import ReminderService

router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.post("/generate", response_model=List[ReminderResponse])
def generate_reminders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[ReminderResponse]:
    service = ReminderService(db)
    reminders = service.generate_reminders_for_organization(str(current_user.organization_id))
    return [ReminderResponse.model_validate(reminder) for reminder in reminders]


@router.get("/", response_model=List[ReminderResponse])
def list_reminders(
    status: Optional[str] = Query(None),
    entity_type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[ReminderResponse]:
    service = ReminderService(db)
    reminders = service.list_reminders(str(current_user.organization_id), status, entity_type, category, search, limit, offset)
    return [ReminderResponse.model_validate(reminder) for reminder in reminders]


@router.get("/unread-count")
def unread_reminder_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, int]:
    service = ReminderService(db)
    count = service.count_unread_reminders(str(current_user.organization_id))
    return {"unread_count": count}


@router.post("/{reminder_id}/read", response_model=ReminderResponse)
def mark_reminder_read(
    reminder_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReminderResponse:
    service = ReminderService(db)
    reminder = service.set_reminder_status(str(current_user.organization_id), reminder_id, "read")
    if reminder is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")
    return ReminderResponse.model_validate(reminder)


@router.post("/{reminder_id}/archive", response_model=ReminderResponse)
def archive_reminder(
    reminder_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReminderResponse:
    service = ReminderService(db)
    reminder = service.set_reminder_status(str(current_user.organization_id), reminder_id, "archived")
    if reminder is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")
    return ReminderResponse.model_validate(reminder)


@router.get("/rules", response_model=List[ReminderRuleResponse])
def list_reminder_rules(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[ReminderRuleResponse]:
    service = ReminderService(db)
    rules = service.list_reminder_rules(str(current_user.organization_id))
    return [ReminderRuleResponse.model_validate(rule) for rule in rules]


@router.post("/rules", response_model=ReminderRuleResponse, status_code=status.HTTP_201_CREATED)
def create_reminder_rule(
    payload: ReminderRuleCreate,
    current_user: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
) -> ReminderRuleResponse:
    service = ReminderService(db)
    rule = service.create_reminder_rule(str(current_user.organization_id), payload.dict(exclude_none=True))
    return ReminderRuleResponse.model_validate(rule)


@router.put("/rules/{rule_id}", response_model=ReminderRuleResponse)
def update_reminder_rule(
    rule_id: int,
    payload: ReminderRuleUpdate,
    current_user: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
) -> ReminderRuleResponse:
    service = ReminderService(db)
    rule = service.update_reminder_rule(str(current_user.organization_id), rule_id, payload.dict(exclude_none=True))
    return ReminderRuleResponse.model_validate(rule)


@router.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reminder_rule(
    rule_id: int,
    current_user: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
) -> None:
    service = ReminderService(db)
    service.delete_reminder_rule(str(current_user.organization_id), rule_id)
    return None


@router.get("/notification-preferences", response_model=List[NotificationPreferenceResponse])
def list_notification_preferences(
    user_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[NotificationPreferenceResponse]:
    service = ReminderService(db)
    preferences = service.list_notification_preferences(str(current_user.organization_id), user_id)
    return [NotificationPreferenceResponse.model_validate(pref) for pref in preferences]


@router.post("/notification-preferences", response_model=NotificationPreferenceResponse, status_code=status.HTTP_201_CREATED)
def upsert_notification_preference(
    payload: NotificationPreferenceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NotificationPreferenceResponse:
    service = ReminderService(db)
    preference = service.upsert_notification_preference(str(current_user.organization_id), payload.dict(exclude_none=True))
    return NotificationPreferenceResponse.model_validate(preference)


@router.get("/notification-events", response_model=List[NotificationEventResponse])
def list_notification_events(
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[NotificationEventResponse]:
    service = ReminderService(db)
    events = service.list_notification_events(str(current_user.organization_id), limit, offset)
    return [NotificationEventResponse.model_validate(event) for event in events]
