from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from ..core.dependencies import get_current_user, require_roles
from ..database import get_db
from ..models import User
from ..schemas.package import (
    TripPackageCreate,
    TripPackageResponse,
    TripPackageUpdate,
)
from ..services import package_service

router = APIRouter(prefix="/trip-packages", tags=["trip-packages"])


@router.post("/", response_model=TripPackageResponse, status_code=status.HTTP_201_CREATED)
def create_package(
    payload: TripPackageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    return package_service.create_package_service(db, current_user, payload)


@router.get("/", response_model=List[TripPackageResponse])
def list_packages(
    db: Session = Depends(get_db),
    active: Optional[bool] = Query(None, description="Filter active packages"),
    category: Optional[str] = Query(None, description="Filter by package category"),
    search: Optional[str] = Query(None, description="Search package names"),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
    current_user: User = Depends(get_current_user),
):
    items, _ = package_service.list_packages_service(
        db,
        current_user,
        active=active,
        category=category,
        search=search,
        page=page,
        page_size=page_size,
    )
    return items


@router.get("/{package_id}", response_model=TripPackageResponse)
def get_package(
    package_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return package_service.get_package_service(db, package_id, current_user)


@router.put("/{package_id}", response_model=TripPackageResponse)
def update_package(
    package_id: int,
    payload: TripPackageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    return package_service.update_package_service(db, package_id, current_user, payload)


@router.delete("/{package_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_package(
    package_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    package_service.delete_package_service(db, package_id, current_user)
