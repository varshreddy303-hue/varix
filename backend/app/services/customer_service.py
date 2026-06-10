from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from uuid import UUID

from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..repositories import customer_repository
from ..models import AuditLog, Customer, User
from ..schemas.customer import CustomerCreate, CustomerUpdate
from .audit_utils import serialize_audit_changes
import uuid


def _create_audit_log(db: Session, user: User, organization_id: str, entity_id: int, action: str, changes: dict) -> AuditLog:
    audit = AuditLog(
        organization_id=uuid.UUID(organization_id) if isinstance(organization_id, str) else organization_id,
        user_id=user.id,
        entity_type="customer",
        entity_id=entity_id,
        action=action,
        changes=serialize_audit_changes(changes),
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit


def create_customer_service(db: Session, current_user: User, payload: CustomerCreate) -> Customer:
    organization_id = str(current_user.organization_id)

    if payload.phone_number:
        existing_phone = customer_repository.get_customer_by_phone(db, payload.phone_number, organization_id)
        if existing_phone:
            raise HTTPException(status_code=409, detail="Phone number already exists for this organization")

    if payload.gst_number:
        existing_gst = customer_repository.get_customer_by_gst(db, payload.gst_number, organization_id)
        if existing_gst:
            raise HTTPException(status_code=409, detail="GST number already exists for this organization")

    customer = Customer(
        organization_id=current_user.organization_id,
        customer_name=payload.customer_name or '',
        phone_number=payload.phone_number or '',
        email=str(payload.email) if payload.email else None,
        gst_number=payload.gst_number,
        address=payload.address,
        city=payload.city,
        state=payload.state,
        pincode=payload.pincode,
        notes=payload.notes,
        is_active=payload.is_active if payload.is_active is not None else True,
    )

    customer = customer_repository.create_customer(db, customer)
    _create_audit_log(db, current_user, organization_id, customer.id, "create", payload.model_dump(exclude_none=True))
    return customer


def get_customer_service(db: Session, customer_id: int, current_user: User) -> Customer:
    organization_id = str(current_user.organization_id)
    customer = customer_repository.get_customer_by_id(db, customer_id, organization_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


def delete_customer_service(db: Session, customer_id: int, current_user: User) -> None:
    organization_id = str(current_user.organization_id)
    customer = customer_repository.get_customer_by_id(db, customer_id, organization_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    customer_repository.soft_delete_customer(db, customer)
    _create_audit_log(db, current_user, organization_id, customer.id, "delete", {"deleted_at": datetime.utcnow().isoformat()})


def update_customer_service(db: Session, customer_id: int, current_user: User, payload: CustomerUpdate):
    organization_id = str(current_user.organization_id)
    customer = customer_repository.get_customer_by_id(db, customer_id, organization_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    if payload.phone_number and payload.phone_number != customer.phone_number:
        if customer_repository.get_customer_by_phone(db, payload.phone_number, organization_id):
            raise HTTPException(status_code=409, detail="Phone number already exists for this organization")

    if payload.gst_number and payload.gst_number != customer.gst_number:
        if customer_repository.get_customer_by_gst(db, payload.gst_number, organization_id):
            raise HTTPException(status_code=409, detail="GST number already exists for this organization")

    update_data: Dict[str, Any] = {k: v for k, v in payload.dict().items() if v is not None}
    customer = customer_repository.update_customer(db, customer, update_data)
    _create_audit_log(db, current_user, organization_id, customer.id, "update", update_data)
    return customer


def list_customers_service(db: Session, current_user: User, name: Optional[str], phone: Optional[str], gst: Optional[str], page: int = 1, page_size: int = 25) -> Tuple[list, int]:
    if page < 1 or page_size < 1:
        raise HTTPException(status_code=400, detail="Invalid pagination parameters")

    organization_id = str(current_user.organization_id)
    offset = (page - 1) * page_size
    items, total = customer_repository.list_customers(
        db,
        organization_id=organization_id,
        name=name,
        phone=phone,
        gst=gst,
        offset=offset,
        limit=page_size,
    )
    return items, total
