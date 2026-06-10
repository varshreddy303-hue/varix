from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import (
    AuditLog,
    Booking,
    Invoice,
    InvoiceItem,
    InvoiceStatusEnum,
    Trip,
    TripStatusEnum,
)
from ..repositories.invoice_repository import InvoiceRepository
from ..schemas.invoice import InvoiceCreate, InvoiceResponse, InvoiceUpdate


class InvoiceService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = InvoiceRepository()

    def _generate_invoice_number(self, organization_id: str) -> str:
        result = self.db.execute(select(Invoice.invoice_number).where(Invoice.organization_id == organization_id))
        used_numbers = sorted(
            {
                int(str(invoice_number).strip())
                for invoice_number in result.scalars()
                if invoice_number is not None and str(invoice_number).strip().isdigit()
            }
        )
        next_number = 10001
        for number in used_numbers:
            if number == next_number:
                next_number += 1
            elif number > next_number:
                break
        return str(next_number)

    def _attach_balance(self, invoice: Invoice) -> None:
        invoice.balance_amount = float(invoice.total_amount or 0.0) - float(invoice.advance_received or 0.0)

    @staticmethod
    def _to_cents(amount: float) -> int:
        return int(round(amount * 100))

    def _load_trip(self, trip_id: int, organization_id: str) -> Trip:
        result = self.db.execute(
            select(Trip).where(
                Trip.id == trip_id,
                Trip.organization_id == organization_id,
            )
        )
        trip = result.scalar_one_or_none()
        if trip is None:
            raise HTTPException(status_code=404, detail="Trip not found")
        return trip

    def _load_booking(self, booking_id: int, organization_id: str) -> Booking:
        booking = self.repository.get_booking_by_id(self.db, booking_id, organization_id)
        if booking is None:
            raise HTTPException(status_code=404, detail="Booking not found")
        return booking

    def _validate_completed_trip(self, trip: Trip) -> None:
        if trip.status != TripStatusEnum.COMPLETED:
            raise HTTPException(status_code=400, detail="Invoice can only be created for completed trips")

    def _assert_unique_invoice_number(self, invoice_number: str, organization_id: str) -> None:
        existing = self.repository.get_invoice_by_number(self.db, invoice_number, organization_id)
        if existing is not None:
            raise HTTPException(status_code=409, detail="invoice_number already exists")

    def _build_invoice_items(self, trip: Trip, organization_id: str) -> list[InvoiceItem]:
        package_amount = float(trip.package_amount or 0.0)
        extra_km_amount = float(trip.extra_km_amount or 0.0)
        extra_hour_amount = float(trip.extra_hour_amount or 0.0)
        driver_bata = float(trip.driver_bata or 0.0)
        night_charges = float(trip.night_charges or 0.0)
        permit_amount = float(trip.permit_amount or 0.0)
        state_tax_amount = float(trip.state_tax_amount or 0.0)
        toll_amount = float(trip.toll_amount or 0.0)
        parking_amount = float(trip.parking_amount or 0.0)
        trip_revenue = float(trip.trip_revenue or 0.0)

        subtotal_without_tax = max(0.0, trip_revenue - state_tax_amount)
        extras_total = extra_km_amount + extra_hour_amount + driver_bata + night_charges + permit_amount + toll_amount + parking_amount
        base_amount = package_amount if package_amount > 0 else max(0.0, subtotal_without_tax - extras_total)
        base_description = trip.package_name or "Trip charges"

        items: list[InvoiceItem] = []
        if base_amount > 0 or trip_revenue > 0:
            items.append(
                InvoiceItem(
                    organization_id=organization_id,
                    description=base_description,
                    quantity=1,
                    unit_price_cents=self._to_cents(base_amount),
                    line_total_cents=self._to_cents(base_amount),
                )
            )

        if extra_km_amount > 0:
            items.append(
                InvoiceItem(
                    organization_id=organization_id,
                    description=f"Extra KM ({trip.extra_km or 0} km)",
                    quantity=1,
                    unit_price_cents=self._to_cents(extra_km_amount),
                    line_total_cents=self._to_cents(extra_km_amount),
                )
            )

        if extra_hour_amount > 0:
            items.append(
                InvoiceItem(
                    organization_id=organization_id,
                    description=f"Extra hours ({trip.extra_hours or 0})",
                    quantity=1,
                    unit_price_cents=self._to_cents(extra_hour_amount),
                    line_total_cents=self._to_cents(extra_hour_amount),
                )
            )

        if driver_bata > 0:
            items.append(
                InvoiceItem(
                    organization_id=organization_id,
                    description="Driver bata",
                    quantity=1,
                    unit_price_cents=self._to_cents(driver_bata),
                    line_total_cents=self._to_cents(driver_bata),
                )
            )

        if night_charges > 0:
            items.append(
                InvoiceItem(
                    organization_id=organization_id,
                    description="Night charges",
                    quantity=1,
                    unit_price_cents=self._to_cents(night_charges),
                    line_total_cents=self._to_cents(night_charges),
                )
            )

        if permit_amount > 0:
            items.append(
                InvoiceItem(
                    organization_id=organization_id,
                    description="Permit charges",
                    quantity=1,
                    unit_price_cents=self._to_cents(permit_amount),
                    line_total_cents=self._to_cents(permit_amount),
                )
            )

        if state_tax_amount > 0:
            items.append(
                InvoiceItem(
                    organization_id=organization_id,
                    description="State tax",
                    quantity=1,
                    unit_price_cents=self._to_cents(state_tax_amount),
                    line_total_cents=self._to_cents(state_tax_amount),
                )
            )

        if toll_amount > 0:
            items.append(
                InvoiceItem(
                    organization_id=organization_id,
                    description="Toll charges",
                    quantity=1,
                    unit_price_cents=self._to_cents(toll_amount),
                    line_total_cents=self._to_cents(toll_amount),
                )
            )

        if parking_amount > 0:
            items.append(
                InvoiceItem(
                    organization_id=organization_id,
                    description="Parking charges",
                    quantity=1,
                    unit_price_cents=self._to_cents(parking_amount),
                    line_total_cents=self._to_cents(parking_amount),
                )
            )

        return items

    def get_invoice(self, invoice_id: int, organization_id: str) -> InvoiceResponse:
        invoice = self.repository.get_invoice_by_id(self.db, invoice_id, organization_id)
        if invoice is None:
            raise HTTPException(status_code=404, detail="Invoice not found")
        self._attach_balance(invoice)
        return InvoiceResponse.from_orm(invoice)

    def list_invoices(
        self,
        organization_id: str,
        customer_id: Optional[int] = None,
        trip_id: Optional[int] = None,
        booking_id: Optional[int] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[InvoiceResponse]:
        invoices = self.repository.list_invoices(
            self.db,
            organization_id=organization_id,
            customer_id=customer_id,
            trip_id=trip_id,
            booking_id=booking_id,
            status=status,
            limit=limit,
            offset=offset,
        )
        for invoice in invoices:
            self._attach_balance(invoice)
        return [InvoiceResponse.from_orm(invoice) for invoice in invoices]

    def create_invoice(self, organization_id: str, payload: InvoiceCreate, user_id: int) -> InvoiceResponse:
        trip = None
        if payload.trip_id is not None:
            trip = self._load_trip(payload.trip_id, organization_id)
            self._validate_completed_trip(trip)

            existing_invoice = self.repository.get_invoice_by_trip(self.db, payload.trip_id, organization_id)
            if existing_invoice is not None:
                raise HTTPException(status_code=409, detail="Invoice already exists for this trip")

        booking = None
        if payload.booking_id is not None:
            booking = self._load_booking(payload.booking_id, organization_id)

        invoice_number = payload.invoice_number or self._generate_invoice_number(organization_id)
        self._assert_unique_invoice_number(invoice_number, organization_id)

        if trip is not None:
            default_tax_amount = float(trip.state_tax_amount or 0.0)
            tax_amount = payload.tax_amount if payload.tax_amount is not None else default_tax_amount
            subtotal = payload.subtotal if payload.subtotal is not None else float(trip.trip_revenue or 0.0) - tax_amount
            advance_received = (
                float(payload.advance_received)
                if payload.advance_received is not None
                else float(trip.advance_received or 0.0)
            )
            customer_id = trip.booking.customer_id
        else:
            tax_amount = payload.tax_amount if payload.tax_amount is not None else 0.0
            subtotal = payload.subtotal if payload.subtotal is not None else float(booking.booking_amount or 0.0)
            advance_received = float(payload.advance_received or 0.0)
            customer_id = booking.customer_id if booking is not None else None

        total_amount = subtotal + tax_amount
        invoice_date = payload.invoice_date or datetime.utcnow()
        due_date = payload.due_date or (invoice_date + timedelta(days=7))

        invoice = Invoice(
            organization_id=organization_id,
            customer_id=customer_id,
            trip_id=payload.trip_id,
            booking_id=payload.booking_id,
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            due_date=due_date,
            subtotal=subtotal,
            tax_amount=tax_amount,
            advance_received=advance_received,
            total_amount=total_amount,
            status=InvoiceStatusEnum.DRAFT,
            notes=payload.notes,
            metadata_json=None,
        )

        if trip is not None:
            invoice.invoice_items = self._build_invoice_items(trip, organization_id)
        else:
            invoice.invoice_items = [
                InvoiceItem(
                    organization_id=organization_id,
                    description="Booking charges",
                    quantity=1,
                    unit_price_cents=self._to_cents(subtotal),
                    line_total_cents=self._to_cents(subtotal),
                )
            ]
        self.repository.create_invoice(self.db, invoice)
        self.db.commit()

        self._attach_balance(invoice)
        self._log_audit(organization_id, user_id, invoice.id, "invoice.created")
        return InvoiceResponse.from_orm(invoice)

    def update_invoice(self, invoice_id: int, organization_id: str, payload: InvoiceUpdate, user_id: int) -> InvoiceResponse:
        invoice = self.repository.get_invoice_by_id(self.db, invoice_id, organization_id)
        if invoice is None:
            raise HTTPException(status_code=404, detail="Invoice not found")
        if invoice.status == InvoiceStatusEnum.PAID:
            raise HTTPException(status_code=400, detail="Paid invoices cannot be updated")

        if payload.invoice_number is not None and payload.invoice_number != invoice.invoice_number:
            self._assert_unique_invoice_number(payload.invoice_number, organization_id)
            invoice.invoice_number = payload.invoice_number

        if payload.invoice_date is not None:
            invoice.invoice_date = payload.invoice_date
        if payload.due_date is not None:
            invoice.due_date = payload.due_date
        if payload.subtotal is not None:
            invoice.subtotal = payload.subtotal
        if payload.tax_amount is not None:
            invoice.tax_amount = payload.tax_amount
        if payload.advance_received is not None:
            invoice.advance_received = payload.advance_received
        if payload.notes is not None:
            invoice.notes = payload.notes

        invoice.total_amount = float(invoice.subtotal or 0.0) + float(invoice.tax_amount or 0.0)
        self._attach_balance(invoice)

        self.repository.update_invoice(self.db, invoice)
        self.db.commit()

        self._log_audit(organization_id, user_id, invoice.id, "invoice.updated")
        return InvoiceResponse.from_orm(invoice)

    def send_invoice(self, invoice_id: int, organization_id: str, user_id: int) -> InvoiceResponse:
        invoice = self.repository.get_invoice_by_id(self.db, invoice_id, organization_id)
        if invoice is None:
            raise HTTPException(status_code=404, detail="Invoice not found")
        if invoice.status == InvoiceStatusEnum.PAID:
            raise HTTPException(status_code=400, detail="Paid invoices cannot be sent")

        invoice.status = InvoiceStatusEnum.SENT
        self.repository.update_invoice(self.db, invoice)
        self.db.commit()

        self._attach_balance(invoice)
        self._log_audit(organization_id, user_id, invoice.id, "invoice.sent")
        return InvoiceResponse.from_orm(invoice)

    def mark_paid(self, invoice_id: int, organization_id: str, user_id: int) -> InvoiceResponse:
        invoice = self.repository.get_invoice_by_id(self.db, invoice_id, organization_id)
        if invoice is None:
            raise HTTPException(status_code=404, detail="Invoice not found")
        if invoice.status == InvoiceStatusEnum.PAID:
            raise HTTPException(status_code=400, detail="Invoice is already paid")

        invoice.status = InvoiceStatusEnum.PAID
        self.repository.update_invoice(self.db, invoice)
        self.db.commit()

        self._attach_balance(invoice)
        self._log_audit(organization_id, user_id, invoice.id, "invoice.paid")
        return InvoiceResponse.from_orm(invoice)

    def _log_audit(self, organization_id: str, user_id: int, invoice_id: int, event: str) -> None:
        audit = AuditLog(
            organization_id=organization_id,
            user_id=user_id,
            entity_type="invoice",
            entity_id=invoice_id,
            action=event,
            changes={},
        )
        self.db.add(audit)
        self.db.commit()
