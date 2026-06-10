from typing import Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..models import TripPackage, User
from ..repositories import package_repository
from ..schemas.package import TripPackageCreate, TripPackageResponse, TripPackageUpdate


def _assert_unique_package_name(db: Session, organization_id: str, name: str, ignore_id: Optional[int] = None) -> None:
    query = db.query(TripPackage).filter(TripPackage.organization_id == organization_id, TripPackage.name == name)
    if ignore_id is not None:
        query = query.filter(TripPackage.id != ignore_id)
    existing = query.first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Package name already exists")


def create_package_service(db: Session, current_user: User, payload: TripPackageCreate) -> TripPackage:
    organization_id = str(current_user.organization_id)
    _assert_unique_package_name(db, organization_id, payload.name)

    package = TripPackage(
        organization_id=current_user.organization_id,
        name=payload.name,
        package_category=payload.package_category,
        included_hours=payload.included_hours,
        included_km=payload.included_km,
        base_amount=payload.base_amount,
        extra_km_rate=payload.extra_km_rate,
        extra_hour_rate=payload.extra_hour_rate,
        driver_bata_default=payload.driver_bata_default,
        night_charge_default=payload.night_charge_default,
        permit_default=payload.permit_default,
        state_tax_default=payload.state_tax_default,
        minimum_km_per_day=payload.minimum_km_per_day,
        km_rate=payload.km_rate,
        active=payload.active,
    )
    return package_repository.create_package(db, package)


def get_package_service(db: Session, package_id: int, current_user: User) -> TripPackage:
    organization_id = str(current_user.organization_id)
    package = package_repository.get_package_by_id(db, package_id, organization_id)
    if not package:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Package not found")
    return package


def list_packages_service(
    db: Session,
    current_user: User,
    active: Optional[bool] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 25,
) -> Tuple[list[TripPackage], int]:
    if page < 1 or page_size < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid pagination parameters")

    organization_id = str(current_user.organization_id)
    offset = (page - 1) * page_size
    return package_repository.list_packages(
        db,
        organization_id=organization_id,
        active=active,
        category=category,
        search=search,
        offset=offset,
        limit=page_size,
    )


def update_package_service(db: Session, package_id: int, current_user: User, payload: TripPackageUpdate) -> TripPackage:
    organization_id = str(current_user.organization_id)
    package = package_repository.get_package_by_id(db, package_id, organization_id)
    if not package:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Package not found")

    values = payload.dict(exclude_none=True)
    if values.get("name"):
        _assert_unique_package_name(db, organization_id, values["name"], ignore_id=package_id)

    return package_repository.update_package(db, package, values)


def delete_package_service(db: Session, package_id: int, current_user: User) -> None:
    organization_id = str(current_user.organization_id)
    package = package_repository.get_package_by_id(db, package_id, organization_id)
    if not package:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Package not found")
    package_repository.delete_package(db, package)
