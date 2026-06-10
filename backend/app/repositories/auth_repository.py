from typing import List, Optional
from sqlalchemy.orm import Session

from ..models import Organization, Permission, Role, User


def get_organization_by_name(db: Session, name: str) -> Optional[Organization]:
    return db.query(Organization).filter(Organization.name == name).first()


def get_users_by_email(db: Session, email: str) -> List[User]:
    return db.query(User).filter(User.email == email).all()


def get_organization_by_id(db: Session, organization_id: str) -> Optional[Organization]:
    return db.query(Organization).filter(Organization.id == organization_id).first()


def create_organization(db: Session, organization: Organization) -> Organization:
    db.add(organization)
    db.commit()
    db.refresh(organization)
    return organization


def get_user_by_email(db: Session, email: str, organization_id: Optional[str] = None) -> Optional[User]:
    query = db.query(User).filter(User.email == email)
    if organization_id:
        query = query.filter(User.organization_id == organization_id)
    return query.first()


def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user: User) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_role_by_name(db: Session, organization_id: str, role_name: str) -> Optional[Role]:
    return (
        db.query(Role)
        .filter(Role.organization_id == organization_id, Role.name == role_name)
        .first()
    )


def create_role(db: Session, role: Role) -> Role:
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


def add_role_to_user(db: Session, user: User, role: Role) -> User:
    if role not in user.roles:
        user.roles.append(role)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def get_permission_by_code(db: Session, code: str) -> Optional[Permission]:
    return db.query(Permission).filter(Permission.code == code).first()


def create_permission(db: Session, permission: Permission) -> Permission:
    db.add(permission)
    db.commit()
    db.refresh(permission)
    return permission


def list_user_roles(user: User) -> List[str]:
    return [role.name for role in user.roles]


def list_user_permissions(user: User) -> List[str]:
    permissions = set()
    for role in user.roles:
        for permission in role.permissions:
            permissions.add(permission.code)
    return sorted(permissions)
