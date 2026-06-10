from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    validate_token,
)
from ..models import Organization, Role, User
from ..repositories.auth_repository import (
    add_role_to_user,
    create_organization,
    create_role,
    create_user,
    get_organization_by_id,
    get_organization_by_name,
    get_role_by_name,
    get_user_by_email,
    get_users_by_email,
    get_user_by_id,
)


def register_organization_service(db: Session, name: str, admin_email: str, admin_password: str) -> Organization:
    existing = get_organization_by_name(db, name)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Organization already exists")

    organization = Organization(name=name)
    organization = create_organization(db, organization)

    admin_role = get_role_by_name(db, str(organization.id), settings.admin_role_name)
    if not admin_role:
        admin_role = create_role(
            db,
            Role(
                organization_id=organization.id,
                name=settings.admin_role_name,
                description="Organization administrator",
            ),
        )

    user = User(
        organization_id=organization.id,
        email=admin_email,
        hashed_password=hash_password(admin_password),
        is_active=True,
        is_superuser=True,
    )
    user = create_user(db, user)
    add_role_to_user(db, user, admin_role)

    try:
        from .reminder_service import ReminderService

        ReminderService(db).ensure_default_rules_for_organization(str(organization.id))
    except Exception:
        pass

    return organization


def register_user_service(db: Session, organization_id: str, email: str, password: str, role_names: Optional[List[str]] = None) -> User:
    organization = get_organization_by_id(db, organization_id)
    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    existing_user = get_user_by_email(db, email, organization_id)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered for this organization")

    user = User(
        organization_id=organization.id,
        email=email,
        hashed_password=hash_password(password),
        is_active=True,
        is_superuser=False,
    )
    user = create_user(db, user)

    if not role_names:
        role_names = [settings.default_user_role]

    for role_name in set(role_names):
        role = get_role_by_name(db, str(organization.id), role_name)
        if not role:
            role = create_role(
                db,
                Role(
                    organization_id=organization.id,
                    name=role_name,
                    description=f"Default role: {role_name}",
                ),
            )
        add_role_to_user(db, user, role)

    return user


def authenticate_user_service(db: Session, organization_id: Optional[str], email: str, password: str) -> dict:
    if organization_id:
        user = get_user_by_email(db, email, organization_id)
    else:
        users = get_users_by_email(db, email)
        if len(users) == 1:
            user = users[0]
        elif len(users) > 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Multiple organizations found for this email. Please specify an organization.",
            )
        else:
            user = None

    if not user or not user.hashed_password or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is disabled")

    organization_id = str(user.organization_id)
    return {
        "access_token": create_access_token(str(user.id), organization_id, [role.name for role in user.roles]),
        "refresh_token": create_refresh_token(str(user.id), organization_id, user.refresh_token_version),
    }


def refresh_access_token_service(db: Session, refresh_token: str) -> dict:
    try:
        payload = validate_token(refresh_token, expected_type="refresh")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user_id = payload.get("sub")
    version = payload.get("version")
    organization_id = payload.get("org_id")

    if not user_id or version is None or not organization_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Malformed refresh token")

    user = get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    if user.refresh_token_version != int(version):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token has been revoked")

    return {
        "access_token": create_access_token(str(user.id), str(organization_id), [role.name for role in user.roles]),
        "refresh_token": create_refresh_token(str(user.id), str(organization_id), user.refresh_token_version),
    }
