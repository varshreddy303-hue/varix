from typing import Optional

from fastapi import APIRouter, Depends, Query

from ..core.dependencies import get_db, get_current_user
from ..schemas.invoice import InvoiceCreate, InvoiceResponse, InvoiceUpdate
from ..services.invoice_service import InvoiceService
from ..services.auth_service import User

router = APIRouter(prefix="/invoices", tags=["Invoices"])


@router.post("/", response_model=InvoiceResponse, status_code=201)
async def create_invoice(
    payload: InvoiceCreate,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
) -> InvoiceResponse:
    service = InvoiceService(db)
    return service.create_invoice(current_user.organization_id, payload, current_user.id)


@router.get("/", response_model=list[InvoiceResponse])
async def list_invoices(
    customer_id: Optional[int] = Query(None),
    trip_id: Optional[int] = Query(None),
    booking_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
) -> list[InvoiceResponse]:
    service = InvoiceService(db)
    return service.list_invoices(
        current_user.organization_id,
        customer_id=customer_id,
        trip_id=trip_id,
        booking_id=booking_id,
        status=status,
        limit=limit,
        offset=offset,
    )


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
) -> InvoiceResponse:
    service = InvoiceService(db)
    return service.get_invoice(invoice_id, current_user.organization_id)


@router.put("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: int,
    payload: InvoiceUpdate,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
) -> InvoiceResponse:
    service = InvoiceService(db)
    return service.update_invoice(invoice_id, current_user.organization_id, payload, current_user.id)


@router.post("/{invoice_id}/send", response_model=InvoiceResponse)
async def send_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
) -> InvoiceResponse:
    service = InvoiceService(db)
    return service.send_invoice(invoice_id, current_user.organization_id, current_user.id)


@router.post("/{invoice_id}/mark-paid", response_model=InvoiceResponse)
async def mark_invoice_paid(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
) -> InvoiceResponse:
    service = InvoiceService(db)
    return service.mark_paid(invoice_id, current_user.organization_id, current_user.id)
