from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from ..models import TripPackage


def get_package_by_id(db: Session, package_id: int, organization_id: Optional[str] = None) -> Optional[TripPackage]:
    query = db.query(TripPackage).filter(TripPackage.id == package_id)
    if organization_id:
        query = query.filter(TripPackage.organization_id == organization_id)
    return query.first()


def list_packages(
    db: Session,
    organization_id: Optional[str] = None,
    active: Optional[bool] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    offset: int = 0,
    limit: int = 50,
) -> Tuple[List[TripPackage], int]:
    query = db.query(TripPackage)

    if organization_id:
        query = query.filter(TripPackage.organization_id == organization_id)
    if active is not None:
        query = query.filter(TripPackage.active == active)
    if category:
        query = query.filter(TripPackage.package_category == category)
    if search:
        search_term = f"%{search.lower()}%"
        query = query.filter(TripPackage.name.ilike(search_term))

    total = query.count()
    packages = query.order_by(TripPackage.name).offset(offset).limit(limit).all()
    return packages, total


def create_package(db: Session, package: TripPackage) -> TripPackage:
    db.add(package)
    db.commit()
    db.refresh(package)
    return package


def update_package(db: Session, package: TripPackage, values: dict) -> TripPackage:
    for key, value in values.items():
        setattr(package, key, value)
    db.add(package)
    db.commit()
    db.refresh(package)
    return package


def delete_package(db: Session, package: TripPackage) -> None:
    db.delete(package)
    db.commit()
