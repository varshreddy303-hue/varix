from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from ..models import (
    NotificationEvent,
    NotificationPreference,
    Reminder,
    ReminderRule,
)


class ReminderRepository:
    EVENT_CATEGORIES = {
        'vehicle_compliance': [
            'insurance_expiry',
            'permit_expiry',
            'fc_expiry',
            'pollution_expiry',
            'road_tax_expiry',
            'gps_subscription_expiry',
            'service_due',
            'tyre_change_due',
            'battery_change_due',
        ],
        'finance': ['emi_due', 'emi_overdue', 'loan_closure'],
        'operations': ['trip_start_today', 'trip_start_tomorrow', 'trip_delayed', 'driver_not_assigned', 'vehicle_not_assigned'],
        'payments': ['invoice_due', 'invoice_overdue', 'payment_pending'],
    }

    @staticmethod
    def create_rule(db: Session, rule: ReminderRule) -> ReminderRule:
        db.add(rule)
        db.commit()
        db.refresh(rule)
        return rule

    @staticmethod
    def get_rule_by_id(db: Session, rule_id: int, organization_id: str) -> Optional[ReminderRule]:
        return (
            db.query(ReminderRule)
            .filter(ReminderRule.id == rule_id, ReminderRule.organization_id == organization_id)
            .first()
        )

    @staticmethod
    def list_rules(db: Session, organization_id: str) -> List[ReminderRule]:
        return (
            db.query(ReminderRule)
            .filter(ReminderRule.organization_id == organization_id)
            .order_by(ReminderRule.priority.asc(), ReminderRule.name.asc())
            .all()
        )

    @staticmethod
    def update_rule(db: Session, rule: ReminderRule, values: dict) -> ReminderRule:
        for key, value in values.items():
            setattr(rule, key, value)
        db.add(rule)
        db.commit()
        db.refresh(rule)
        return rule

    @staticmethod
    def delete_rule(db: Session, rule: ReminderRule) -> None:
        db.delete(rule)
        db.commit()

    @staticmethod
    def get_existing_reminder(
        db: Session,
        organization_id: str,
        rule_id: int,
        entity_type: Optional[str],
        entity_id: Optional[int],
        reminder_date: datetime,
    ) -> Optional[Reminder]:
        return (
            db.query(Reminder)
            .filter(
                Reminder.organization_id == organization_id,
                Reminder.rule_id == rule_id,
                Reminder.entity_type == entity_type,
                Reminder.entity_id == entity_id,
                Reminder.reminder_date == reminder_date,
            )
            .first()
        )

    @staticmethod
    def create_reminder(db: Session, reminder: Reminder) -> Reminder:
        db.add(reminder)
        db.commit()
        db.refresh(reminder)
        return reminder

    @staticmethod
    def list_reminders(
        db: Session,
        organization_id: str,
        status: Optional[str] = None,
        entity_type: Optional[str] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Reminder]:
        query = db.query(Reminder).filter(Reminder.organization_id == organization_id)
        if status is not None:
            query = query.filter(Reminder.status == status)
        if entity_type is not None:
            query = query.filter(Reminder.entity_type == entity_type)
        if category is not None:
            event_types = ReminderRepository.EVENT_CATEGORIES.get(category.lower())
            if event_types is not None:
                query = query.join(ReminderRule).filter(ReminderRule.event_type.in_(event_types))
        if search is not None:
            query = query.filter(Reminder.message.ilike(f"%{search}%"))
        return query.order_by(Reminder.reminder_date.desc()).offset(offset).limit(limit).all()

    @staticmethod
    def count_unread_reminders(db: Session, organization_id: str) -> int:
        return db.query(Reminder).filter(Reminder.organization_id == organization_id, Reminder.status == 'pending').count()

    @staticmethod
    def get_reminder_by_id(db: Session, reminder_id: int, organization_id: str) -> Optional[Reminder]:
        return (
            db.query(Reminder)
            .filter(Reminder.id == reminder_id, Reminder.organization_id == organization_id)
            .first()
        )

    @staticmethod
    def update_reminder(db: Session, reminder: Reminder) -> Reminder:
        db.add(reminder)
        db.commit()
        db.refresh(reminder)
        return reminder

    @staticmethod
    def list_notification_preferences(
        db: Session,
        organization_id: str,
        user_id: Optional[str] = None,
    ) -> List[NotificationPreference]:
        query = db.query(NotificationPreference).filter(NotificationPreference.organization_id == organization_id)
        if user_id is not None:
            query = query.filter(NotificationPreference.user_id == user_id)
        return query.order_by(NotificationPreference.event_type.asc(), NotificationPreference.channel.asc()).all()

    @staticmethod
    def get_notification_preference(
        db: Session,
        organization_id: str,
        user_id: Optional[str],
        event_type: str,
        channel: str,
    ) -> Optional[NotificationPreference]:
        return (
            db.query(NotificationPreference)
            .filter(
                NotificationPreference.organization_id == organization_id,
                NotificationPreference.user_id == user_id,
                NotificationPreference.event_type == event_type,
                NotificationPreference.channel == channel,
            )
            .first()
        )

    @staticmethod
    def upsert_notification_preference(
        db: Session,
        preference: NotificationPreference,
    ) -> NotificationPreference:
        db.add(preference)
        db.commit()
        db.refresh(preference)
        return preference

    @staticmethod
    def create_notification_event(db: Session, event: NotificationEvent) -> NotificationEvent:
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def list_notification_events(
        db: Session,
        organization_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> List[NotificationEvent]:
        return (
            db.query(NotificationEvent)
            .filter(NotificationEvent.organization_id == organization_id)
            .order_by(NotificationEvent.scheduled_time.desc().nullslast(), NotificationEvent.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_notification_event(
        db: Session,
        reminder_id: int,
        event_type: str,
        channel: str,
    ) -> Optional[NotificationEvent]:
        return (
            db.query(NotificationEvent)
            .filter(
                NotificationEvent.reminder_id == reminder_id,
                NotificationEvent.event_type == event_type,
                NotificationEvent.channel == channel,
            )
            .first()
        )
