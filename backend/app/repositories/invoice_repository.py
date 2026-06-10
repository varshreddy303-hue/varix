from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from ..models import Booking, Invoice


class InvoiceRepository:
    @staticmethod
    def get_invoice_by_id(db: Session, invoice_id: int, organization_id: str) -> Optional[Invoice]:
        result = db.execute(
            select(Invoice).where(
                and_(Invoice.id == invoice_id, Invoice.organization_id == organization_id)
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    def get_invoice_by_number(db: Session, invoice_number: str, organization_id: str) -> Optional[Invoice]:
        result = db.execute(
            select(Invoice).where(
                and_(Invoice.invoice_number == invoice_number, Invoice.organization_id == organization_id)
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    def get_booking_by_id(db: Session, booking_id: int, organization_id: str) -> Optional[Booking]:
        result = db.execute(
            select(Booking).where(
                and_(Booking.id == booking_id, Booking.organization_id == organization_id)
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    def get_invoice_by_trip(db: Session, trip_id: int, organization_id: str) -> Optional[Invoice]:
        result = db.execute(
            select(Invoice).where(
                and_(Invoice.trip_id == trip_id, Invoice.organization_id == organization_id)
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    def list_invoices(
        db: Session,
        organization_id: str,
        customer_id: Optional[int] = None,
        trip_id: Optional[int] = None,
        booking_id: Optional[int] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Invoice]:
        query = select(Invoice).where(Invoice.organization_id == organization_id)

        if customer_id is not None:
            query = query.where(Invoice.customer_id == customer_id)
        if trip_id is not None:
            query = query.where(Invoice.trip_id == trip_id)
        if booking_id is not None:
            query = query.where(Invoice.booking_id == booking_id)
        if status is not None:
            query = query.where(Invoice.status == status)

        result = db.execute(query.limit(limit).offset(offset))
        return result.scalars().all()

    @staticmethod
    def create_invoice(db: Session, invoice: Invoice) -> Invoice:
        db.add(invoice)
        db.flush()
        return invoice

    @staticmethod
    def update_invoice(db: Session, invoice: Invoice) -> Invoice:
        db.flush()
        return invoice
