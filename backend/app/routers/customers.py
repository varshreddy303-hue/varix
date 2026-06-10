from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional
from sqlalchemy.orm import Session

from ..database import get_db
from ..core.dependencies import get_current_user, require_roles
from ..models import User
from ..schemas.customer import CustomerCreate, CustomerResponse, CustomerUpdate
from ..services import customer_service

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(
    payload: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    customer = customer_service.create_customer_service(db, current_user, payload)
    return customer


@router.get("/", response_model=List[CustomerResponse])
def list_customers(
    db: Session = Depends(get_db),
    name: Optional[str] = Query(None, description="Search by customer name"),
    phone: Optional[str] = Query(None, description="Search by phone number"),
    gst: Optional[str] = Query(None, description="Search by GST number"),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
    current_user: User = Depends(get_current_user),
):
    items, total = customer_service.list_customers_service(db, current_user, name, phone, gst, page, page_size)
    return items


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer = customer_service.get_customer_service(db, customer_id, current_user)
    return customer


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    customer = customer_service.update_customer_service(db, customer_id, current_user, payload)
    return customer


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    customer_service.delete_customer_service(db, customer_id, current_user)
    return None
