from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_
from ..models import AuditLog, Customer
from datetime import datetime


def get_customer_by_id(db: Session, customer_id: int, organization_id: Optional[str] = None) -> Optional[Customer]:
    q = db.query(Customer).filter(Customer.id == customer_id, Customer.deleted_at.is_(None))
    if organization_id:
        q = q.filter(Customer.organization_id == organization_id)
    return q.first()


def get_customer_by_phone(db: Session, phone_number: str, organization_id: Optional[str] = None) -> Optional[Customer]:
    q = db.query(Customer).filter(Customer.phone_number == phone_number, Customer.deleted_at.is_(None))
    if organization_id:
        q = q.filter(Customer.organization_id == organization_id)
    return q.first()


def get_customer_by_gst(db: Session, gst_number: str, organization_id: Optional[str] = None) -> Optional[Customer]:
    q = db.query(Customer).filter(Customer.gst_number == gst_number, Customer.deleted_at.is_(None))
    if organization_id:
        q = q.filter(Customer.organization_id == organization_id)
    return q.first()


def create_customer(db: Session, customer: Customer) -> Customer:
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def update_customer(db: Session, customer: Customer, values: dict) -> Customer:
    for k, v in values.items():
        setattr(customer, k, v)
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def soft_delete_customer(db: Session, customer: Customer) -> Customer:
    customer.deleted_at = datetime.utcnow()
    customer.is_active = False
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def list_customers(
    db: Session,
    organization_id: Optional[str] = None,
    name: Optional[str] = None,
    phone: Optional[str] = None,
    gst: Optional[str] = None,
    offset: int = 0,
    limit: int = 50,
) -> Tuple[List[Customer], int]:
    q = db.query(Customer).filter(Customer.deleted_at.is_(None))
    if organization_id:
        q = q.filter(Customer.organization_id == organization_id)
    if name:
        q = q.filter(Customer.customer_name.ilike(f"%{name}%"))
    if phone:
        q = q.filter(Customer.phone_number.ilike(f"%{phone}%"))
    if gst:
        q = q.filter(Customer.gst_number.ilike(f"%{gst}%"))

    total = q.count()
    items = q.order_by(Customer.created_at.desc()).offset(offset).limit(limit).all()
    return items, total
