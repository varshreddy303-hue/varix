from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from ..models import (
    Booking,
    Invoice,
    InvoiceStatusEnum,
    NotificationEvent,
    NotificationPreference,
    Reminder,
    ReminderRule,
    Trip,
    TripStatusEnum,
    Vehicle,
)
from ..repositories.reminder_repository import ReminderRepository
from .vehicle_service import _calculate_next_emi_due_datetime


DEFAULT_REMINDER_RULES: List[Dict[str, Any]] = [
    {
        "name": "Trip starting today",
        "category": "operations",
        "event_type": "trip_start_today",
        "description": "Remind the operations team about trips starting today.",
        "trigger_days_before": 0,
        "priority": 10,
    },
    {
        "name": "Trip starting tomorrow",
        "category": "operations",
        "event_type": "trip_start_tomorrow",
        "description": "Remind the operations team one day before trip start.",
        "trigger_days_before": 1,
        "priority": 20,
    },
    {
        "name": "Delayed trip",
        "category": "operations",
        "event_type": "trip_delayed",
        "description": "Flag trips that have not started after scheduled departure.",
        "threshold_hours": 1,
        "priority": 25,
    },
    {
        "name": "Driver not assigned",
        "category": "operations",
        "event_type": "driver_not_assigned",
        "description": "Remind the operations team to assign a driver before trip start.",
        "trigger_days_before": 7,
        "priority": 30,
    },
    {
        "name": "Vehicle not assigned",
        "category": "operations",
        "event_type": "vehicle_not_assigned",
        "description": "Remind the operations team to assign a vehicle before trip start.",
        "trigger_days_before": 7,
        "priority": 40,
    },
    {
        "name": "Invoice due soon",
        "category": "payments",
        "event_type": "invoice_due",
        "description": "Remind the finance team when invoices are due soon.",
        "trigger_days_before": 7,
        "priority": 50,
    },
    {
        "name": "Invoice overdue",
        "category": "payments",
        "event_type": "invoice_overdue",
        "description": "Notify the finance team when invoices are overdue.",
        "priority": 55,
    },
    {
        "name": "Customer payment pending",
        "category": "payments",
        "event_type": "payment_pending",
        "description": "Help the finance team follow up on pending customer payments.",
        "trigger_days_before": 30,
        "priority": 60,
    },
    {
        "name": "Insurance expiry",
        "category": "compliance",
        "event_type": "insurance_expiry",
        "description": "Reminder: fleet managers should renew vehicle insurance before expiry.",
        "trigger_days_before": 30,
        "priority": 70,
    },
    {
        "name": "Permit expiry",
        "category": "compliance",
        "event_type": "permit_expiry",
        "description": "Reminder: fleet managers should renew vehicle permits before expiry.",
        "trigger_days_before": 30,
        "priority": 75,
    },
    {
        "name": "Fitness certificate expiry",
        "category": "compliance",
        "event_type": "fc_expiry",
        "description": "Reminder: fleet managers should renew fitness certificates before expiry.",
        "trigger_days_before": 30,
        "priority": 80,
    },
    {
        "name": "Pollution certificate expiry",
        "category": "compliance",
        "event_type": "pollution_expiry",
        "description": "Reminder: fleet managers should renew pollution certificates before expiry.",
        "trigger_days_before": 30,
        "priority": 85,
    },
    {
        "name": "Road tax expiry",
        "category": "compliance",
        "event_type": "road_tax_expiry",
        "description": "Reminder: fleet managers should renew road tax before expiry.",
        "trigger_days_before": 30,
        "priority": 90,
    },
    {
        "name": "GPS subscription expiry",
        "category": "compliance",
        "event_type": "gps_subscription_expiry",
        "description": "Reminder: fleet managers should renew GPS subscriptions before expiry.",
        "trigger_days_before": 30,
        "priority": 100,
    },
    {
        "name": "Service due",
        "category": "compliance",
        "event_type": "service_due",
        "description": "Reminder: fleet managers should service vehicles before due date.",
        "trigger_days_before": 7,
        "priority": 110,
    },
    {
        "name": "Tyre change due",
        "category": "compliance",
        "event_type": "tyre_change_due",
        "description": "Reminder: fleet managers should perform tyre servicing before due date.",
        "trigger_days_before": 7,
        "priority": 120,
    },
    {
        "name": "Battery change due",
        "category": "compliance",
        "event_type": "battery_change_due",
        "description": "Reminder: fleet managers should schedule battery replacement before due date.",
        "trigger_days_before": 7,
        "priority": 130,
    },
    {
        "name": "EMI due soon",
        "category": "finance",
        "event_type": "emi_due",
        "description": "Reminder: finance should prepare for upcoming EMI payments.",
        "trigger_days_before": 7,
        "priority": 140,
    },
    {
        "name": "EMI overdue",
        "category": "finance",
        "event_type": "emi_overdue",
        "description": "Notify the finance team when EMI payments are overdue.",
        "priority": 145,
    },
    {
        "name": "Loan closure",
        "category": "finance",
        "event_type": "loan_closure",
        "description": "Reminder: finance should review vehicles nearing loan closure.",
        "trigger_days_before": 30,
        "priority": 150,
    },
]


class ReminderService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = ReminderRepository()

    def ensure_default_rules_for_organization(self, organization_id: str) -> None:
        existing_rules = self.repository.list_rules(self.db, organization_id)
        if existing_rules:
            return

        for rule_data in DEFAULT_REMINDER_RULES:
            rule = ReminderRule(
                organization_id=organization_id,
                name=rule_data["name"],
                category=rule_data["category"],
                event_type=rule_data["event_type"],
                description=rule_data.get("description"),
                active=rule_data.get("active", True),
                trigger_days_before=rule_data.get("trigger_days_before"),
                threshold_hours=rule_data.get("threshold_hours"),
                priority=rule_data.get("priority", 100),
                settings=rule_data.get("settings"),
            )
            self.repository.create_rule(self.db, rule)

    def list_reminder_rules(self, organization_id: str) -> List[ReminderRule]:
        return self.repository.list_rules(self.db, organization_id)

    def create_reminder_rule(self, organization_id: str, payload: Dict[str, Any]) -> ReminderRule:
        rule = ReminderRule(organization_id=organization_id, **payload)
        return self.repository.create_rule(self.db, rule)

    def update_reminder_rule(self, organization_id: str, rule_id: int, payload: Dict[str, Any]) -> ReminderRule:
        from fastapi import HTTPException, status

        rule = self.repository.get_rule_by_id(self.db, rule_id, organization_id)
        if not rule:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder rule not found")
        values = {k: v for k, v in payload.items() if v is not None}
        return self.repository.update_rule(self.db, rule, values)

    def delete_reminder_rule(self, organization_id: str, rule_id: int) -> None:
        from fastapi import HTTPException, status

        rule = self.repository.get_rule_by_id(self.db, rule_id, organization_id)
        if not rule:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder rule not found")
        self.repository.delete_rule(self.db, rule)

    def list_reminders(
        self,
        organization_id: str,
        status: Optional[str] = None,
        entity_type: Optional[str] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Reminder]:
        return self.repository.list_reminders(self.db, organization_id, status, entity_type, category, search, limit, offset)

    def count_unread_reminders(self, organization_id: str) -> int:
        return self.repository.count_unread_reminders(self.db, organization_id)

    def set_reminder_status(self, organization_id: str, reminder_id: int, status: str) -> Optional[Reminder]:
        reminder = self.repository.get_reminder_by_id(self.db, reminder_id, organization_id)
        if reminder is None:
            return None
        reminder.status = status
        return self.repository.update_reminder(self.db, reminder)

    def list_notification_preferences(
        self,
        organization_id: str,
        user_id: Optional[str] = None,
    ) -> List[NotificationPreference]:
        return self.repository.list_notification_preferences(self.db, organization_id, user_id)

    def _normalize_datetime(self, dt: Optional[datetime]) -> Optional[datetime]:
        if dt is None:
            return None
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    def upsert_notification_preference(self, organization_id: str, payload: Dict[str, Any]) -> NotificationPreference:
        existing = self.repository.get_notification_preference(
            self.db,
            organization_id,
            payload.get("user_id"),
            payload["event_type"],
            payload["channel"],
        )
        if existing:
            existing.enabled = payload.get("enabled", existing.enabled)
            existing.metadata_json = payload.get("metadata")
            return self.repository.upsert_notification_preference(self.db, existing)

        preference = NotificationPreference(
            organization_id=organization_id,
            user_id=payload.get("user_id"),
            event_type=payload["event_type"],
            channel=payload["channel"],
            enabled=payload.get("enabled", True),
            metadata_json=payload.get("metadata"),
        )
        return self.repository.upsert_notification_preference(self.db, preference)

    def list_notification_events(
        self,
        organization_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> List[NotificationEvent]:
        return self.repository.list_notification_events(self.db, organization_id, limit, offset)

    def generate_reminders_for_organization(self, organization_id: str, now: Optional[datetime] = None) -> List[Reminder]:
        if now is None:
            now = datetime.now(timezone.utc)
        else:
            now = self._normalize_datetime(now)

        self.ensure_default_rules_for_organization(organization_id)
        rules = self.repository.list_rules(self.db, organization_id)
        results: List[Reminder] = []

        for rule in rules:
            if not rule.active:
                continue
            results.extend(self._generate_for_rule(rule, organization_id, now))

        return results

    def _generate_for_rule(self, rule: ReminderRule, organization_id: str, now: datetime) -> List[Reminder]:
        reminders: List[Reminder] = []
        if rule.event_type == "trip_start_today":
            reminders = self._generate_trip_reminders(organization_id, now, 0, 1, rule)
        elif rule.event_type == "trip_start_tomorrow":
            reminders = self._generate_trip_reminders(organization_id, now, 1, 2, rule)
        elif rule.event_type == "trip_delayed":
            reminders = self._generate_trip_delayed_reminders(organization_id, now, rule)
        elif rule.event_type == "driver_not_assigned":
            reminders = self._generate_driver_assignment_reminders(organization_id, now, rule)
        elif rule.event_type == "vehicle_not_assigned":
            reminders = self._generate_vehicle_assignment_reminders(organization_id, now, rule)
        elif rule.event_type == "invoice_due":
            reminders = self._generate_invoice_due_reminders(organization_id, now, rule)
        elif rule.event_type == "invoice_overdue":
            reminders = self._generate_invoice_overdue_reminders(organization_id, now, rule)
        elif rule.event_type == "payment_pending":
            reminders = self._generate_payment_pending_reminders(organization_id, now, rule)
        elif rule.event_type in {
            "insurance_expiry",
            "permit_expiry",
            "fc_expiry",
            "pollution_expiry",
            "road_tax_expiry",
            "gps_subscription_expiry",
            "service_due",
            "tyre_change_due",
            "battery_change_due",
        }:
            reminders = self._generate_vehicle_compliance_reminders(organization_id, now, rule)
        elif rule.event_type in {"emi_due", "emi_overdue", "loan_closure"}:
            reminders = self._generate_finance_reminders(organization_id, now, rule)

        created_reminders = []
        for reminder, created in reminders:
            if created:
                self._create_notification_events(reminder, rule)
            created_reminders.append(reminder)

        return created_reminders

    def _generate_trip_reminders(
        self,
        organization_id: str,
        now: datetime,
        start_offset: int,
        end_offset: int,
        rule: ReminderRule,
    ) -> list[tuple[Reminder, bool]]:
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        start_at = start_of_day + timedelta(days=start_offset)
        end_at = start_of_day + timedelta(days=end_offset)
        trips = (
            self.db.query(Trip)
            .filter(
                Trip.organization_id == organization_id,
                Trip.start_time.is_not(None),
                Trip.start_time >= start_at,
                Trip.start_time < end_at,
                Trip.status.in_([TripStatusEnum.PENDING, TripStatusEnum.ONGOING]),
            )
            .all()
        )
        reminders: list[tuple[Reminder, bool]] = []
        for trip in trips:
            trip_start = self._normalize_datetime(trip.start_time)
            if trip_start is None:
                continue
            reminder_date = start_at if rule.trigger_days_before == 0 else (trip_start - timedelta(days=rule.trigger_days_before))
            if reminder_date < now:
                reminder_date = now
            reminders.append(self._create_reminder_for_entity(rule, "trip", trip.id, reminder_date, trip_start, trip_start))
        return reminders

    def _generate_trip_delayed_reminders(self, organization_id: str, now: datetime, rule: ReminderRule) -> list[tuple[Reminder, bool]]:
        delay_window = timedelta(hours=rule.threshold_hours or 1)
        trips = (
            self.db.query(Trip)
            .filter(
                Trip.organization_id == organization_id,
                Trip.start_time.is_not(None),
                Trip.start_time < now - delay_window,
                Trip.status.in_([TripStatusEnum.PENDING, TripStatusEnum.ONGOING]),
            )
            .all()
        )
        reminders: list[tuple[Reminder, bool]] = []
        for trip in trips:
            trip_start = self._normalize_datetime(trip.start_time)
            if trip_start is None:
                continue
            reminder_date = now
            reminders.append(self._create_reminder_for_entity(rule, "trip", trip.id, reminder_date, trip_start, trip_start))
        return reminders

    def _generate_driver_assignment_reminders(self, organization_id: str, now: datetime, rule: ReminderRule) -> list[tuple[Reminder, bool]]:
        window_end = now + timedelta(days=(rule.trigger_days_before or 7))
        bookings = (
            self.db.query(Booking)
            .filter(
                Booking.organization_id == organization_id,
                Booking.start_date >= now,
                Booking.start_date < window_end,
                Booking.driver_id.is_(None),
            )
            .all()
        )
        reminders: list[tuple[Reminder, bool]] = []
        for booking in bookings:
            booking_start = self._normalize_datetime(booking.start_date)
            if booking_start is None:
                continue
            reminder_date = booking_start - timedelta(days=(rule.trigger_days_before or 7))
            if reminder_date < now:
                reminder_date = now
            reminders.append(self._create_reminder_for_entity(rule, "booking", booking.id, reminder_date, booking_start, booking_start))
        return reminders

    def _generate_vehicle_assignment_reminders(self, organization_id: str, now: datetime, rule: ReminderRule) -> list[tuple[Reminder, bool]]:
        window_end = now + timedelta(days=(rule.trigger_days_before or 7))
        bookings = (
            self.db.query(Booking)
            .filter(
                Booking.organization_id == organization_id,
                Booking.start_date >= now,
                Booking.start_date < window_end,
                Booking.vehicle_id.is_(None),
            )
            .all()
        )
        reminders: list[tuple[Reminder, bool]] = []
        for booking in bookings:
            booking_start = self._normalize_datetime(booking.start_date)
            if booking_start is None:
                continue
            reminder_date = booking_start - timedelta(days=(rule.trigger_days_before or 7))
            if reminder_date < now:
                reminder_date = now
            reminders.append(self._create_reminder_for_entity(rule, "booking", booking.id, reminder_date, booking_start, booking_start))
        return reminders

    def _generate_invoice_due_reminders(self, organization_id: str, now: datetime, rule: ReminderRule) -> list[tuple[Reminder, bool]]:
        window_end = now + timedelta(days=(rule.trigger_days_before or 7))
        invoices = (
            self.db.query(Invoice)
            .filter(
                Invoice.organization_id == organization_id,
                Invoice.due_date.is_not(None),
                Invoice.status != InvoiceStatusEnum.PAID,
                Invoice.due_date >= now,
                Invoice.due_date <= window_end,
            )
            .all()
        )
        reminders: list[tuple[Reminder, bool]] = []
        for invoice in invoices:
            invoice_due = self._normalize_datetime(invoice.due_date)
            if invoice_due is None:
                continue
            reminder_date = invoice_due - timedelta(days=(rule.trigger_days_before or 7))
            if reminder_date < now:
                reminder_date = now
            reminders.append(self._create_reminder_for_entity(rule, "invoice", invoice.id, reminder_date, invoice_due, invoice_due))
        return reminders

    def _generate_invoice_overdue_reminders(self, organization_id: str, now: datetime, rule: ReminderRule) -> list[tuple[Reminder, bool]]:
        invoices = (
            self.db.query(Invoice)
            .filter(
                Invoice.organization_id == organization_id,
                Invoice.due_date.is_not(None),
                Invoice.status != InvoiceStatusEnum.PAID,
                Invoice.due_date < now,
            )
            .all()
        )
        reminders: list[tuple[Reminder, bool]] = []
        for invoice in invoices:
            invoice_due = self._normalize_datetime(invoice.due_date)
            if invoice_due is None:
                continue
            reminders.append(self._create_reminder_for_entity(rule, "invoice", invoice.id, now, invoice_due, invoice_due))
        return reminders

    def _generate_payment_pending_reminders(self, organization_id: str, now: datetime, rule: ReminderRule) -> list[tuple[Reminder, bool]]:
        window_end = now + timedelta(days=(rule.trigger_days_before or 30))
        invoices = (
            self.db.query(Invoice)
            .filter(
                Invoice.organization_id == organization_id,
                Invoice.due_date.is_not(None),
                Invoice.status != InvoiceStatusEnum.PAID,
                Invoice.due_date >= now,
                Invoice.due_date <= window_end,
            )
            .all()
        )
        reminders: list[tuple[Reminder, bool]] = []
        for invoice in invoices:
            invoice_due = self._normalize_datetime(invoice.due_date)
            if invoice_due is None:
                continue
            reminder_date = now
            reminders.append(self._create_reminder_for_entity(rule, "invoice", invoice.id, reminder_date, invoice_due, invoice_due))
        return reminders

    def _generate_vehicle_compliance_reminders(
        self,
        organization_id: str,
        now: datetime,
        rule: ReminderRule,
    ) -> list[tuple[Reminder, bool]]:
        field_name = {
            "insurance_expiry": "insurance_expiry_date",
            "permit_expiry": "permit_expiry_date",
            "fc_expiry": "fc_expiry_date",
            "pollution_expiry": "pollution_expiry_date",
            "road_tax_expiry": "road_tax_expiry_date",
            "gps_subscription_expiry": "gps_subscription_expiry_date",
            "service_due": "service_due_date",
            "tyre_change_due": "tyre_change_due_date",
            "battery_change_due": "battery_change_due_date",
        }.get(rule.event_type)

        if not field_name:
            return []

        window_end = now + timedelta(days=(rule.trigger_days_before or 30))
        filter_field = getattr(Vehicle, field_name)
        vehicles = (
            self.db.query(Vehicle)
            .filter(
                Vehicle.organization_id == organization_id,
                Vehicle.deleted_at.is_(None),
                filter_field.is_not(None),
                filter_field >= now,
                filter_field <= window_end,
            )
            .all()
        )
        reminders: list[tuple[Reminder, bool]] = []
        for vehicle in vehicles:
            vehicle_date = self._normalize_datetime(getattr(vehicle, field_name))
            if vehicle_date is None:
                continue
            reminder_date = vehicle_date - timedelta(days=(rule.trigger_days_before or 30))
            if reminder_date < now:
                reminder_date = now
            reminders.append(self._create_reminder_for_entity(rule, "vehicle", vehicle.id, reminder_date, vehicle_date, vehicle_date))
        return reminders

    def _generate_finance_reminders(self, organization_id: str, now: datetime, rule: ReminderRule) -> list[tuple[Reminder, bool]]:
        vehicles = (
            self.db.query(Vehicle)
            .filter(
                Vehicle.organization_id == organization_id,
                Vehicle.deleted_at.is_(None),
                Vehicle.is_active.is_(True),
                Vehicle.emi_due_day.is_not(None),
            )
            .all()
        )
        reminders: list[tuple[Reminder, bool]] = []
        for vehicle in vehicles:
            next_due = _calculate_next_emi_due_datetime(now.date(), vehicle.emi_due_day)
            next_due = self._normalize_datetime(next_due)
            if next_due is None:
                continue
            if rule.event_type == "emi_due":
                window_start = now
                window_end = now + timedelta(days=(rule.trigger_days_before or 7))
                if window_start <= next_due <= window_end:
                    reminder_date = max(now, next_due - timedelta(days=(rule.trigger_days_before or 7)))
                    reminders.append(self._create_reminder_for_entity(rule, "vehicle", vehicle.id, reminder_date, next_due, next_due))
            elif rule.event_type == "emi_overdue":
                if next_due < now:
                    reminders.append(self._create_reminder_for_entity(rule, "vehicle", vehicle.id, now, next_due, next_due))
            elif rule.event_type == "loan_closure":
                if getattr(vehicle, "loan_closure_date", None) is None:
                    continue
                loan_closure_date = self._normalize_datetime(getattr(vehicle, "loan_closure_date"))
                if loan_closure_date is None:
                    continue
                if loan_closure_date >= now and loan_closure_date <= now + timedelta(days=(rule.trigger_days_before or 30)):
                    reminder_date = max(now, loan_closure_date - timedelta(days=(rule.trigger_days_before or 30)))
                    reminders.append(self._create_reminder_for_entity(rule, "vehicle", vehicle.id, reminder_date, loan_closure_date, loan_closure_date))
        return reminders

    def _create_reminder_for_entity(
        self,
        rule: ReminderRule,
        entity_type: str,
        entity_id: int,
        reminder_date: datetime,
        due_date: Optional[datetime],
        source_date: Optional[datetime],
    ) -> tuple[Reminder, bool]:
        existing = self.repository.get_existing_reminder(
            self.db,
            str(rule.organization_id),
            rule.id,
            entity_type,
            entity_id,
            reminder_date,
        )
        if existing is not None:
            return existing, False

        reminder = Reminder(
            organization_id=rule.organization_id,
            rule_id=rule.id,
            entity_type=entity_type,
            entity_id=entity_id,
            reminder_date=reminder_date,
            due_date=due_date,
            status="pending",
            message=rule.description or f"Reminder: {rule.name}",
            payload={"source_date": source_date.isoformat() if source_date else None, "event_type": rule.event_type},
        )
        return self.repository.create_reminder(self.db, reminder), True

    def _create_notification_events(self, reminder: Reminder, rule: ReminderRule) -> None:
        preferences = self.repository.list_notification_preferences(self.db, str(reminder.organization_id))
        channels = [pref.channel for pref in preferences if pref.enabled and pref.event_type == rule.event_type]
        if not channels:
            channels = ["in_app"]

        for channel in channels:
            existing_event = self.repository.get_notification_event(
                self.db,
                reminder.id,
                rule.event_type,
                channel,
            )
            if existing_event is not None:
                continue

            event = NotificationEvent(
                organization_id=reminder.organization_id,
                reminder_id=reminder.id,
                event_type=rule.event_type,
                recipient_id=None,
                channel=channel,
                status="pending",
                scheduled_time=reminder.reminder_date,
                payload={"reminder_id": reminder.id, "message": reminder.message, "event_type": rule.event_type},
            )
            self.repository.create_notification_event(self.db, event)
