from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.auth import (
    AuthTokenResponse,
    LoginRequest,
    RefreshTokenRequest,
    UserCreate,
    UserResponse,
)
from ..schemas.organization import OrganizationRegistrationRequest, OrganizationResponse
from ..services import auth_service
from ..services.auth_service import refresh_access_token_service
from ..core.security import validate_token

router = APIRouter(prefix="/auth", tags=["auth"])


def resolve_organization_id(x_organization_id: Optional[str] = Header(None)) -> Optional[str]:
    return x_organization_id


def parse_authorization_token(authorization: Optional[str]) -> Dict[str, Any]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization header")
    token = authorization.split(" ", 1)[1]
    try:
        return validate_token(token, expected_type="access")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def require_roles(*allowed_roles: str):
    def dependency(
        authorization: Optional[str] = Header(None),
        x_organization_id: Optional[str] = Header(None),
    ) -> Dict[str, Any]:
        payload = parse_authorization_token(authorization)
        if x_organization_id and payload.get("org_id") != x_organization_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization mismatch")

        user_roles = payload.get("roles", [])
        if not any(role in user_roles for role in allowed_roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return payload

    return dependency


@router.post("/login", response_model=AuthTokenResponse)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
    x_organization_id: Optional[str] = Depends(resolve_organization_id),
):
    organization_id = str(payload.organization_id) if payload.organization_id else (str(x_organization_id) if x_organization_id else None)
    token_pair = auth_service.authenticate_user_service(db, organization_id, payload.email, payload.password)
    return AuthTokenResponse(**token_pair)


@router.post("/refresh", response_model=AuthTokenResponse)
def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    token_pair = refresh_access_token_service(db, payload.refresh_token)
    return AuthTokenResponse(**token_pair)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_roles("admin")),
):
    organization_id = current_user.get("org_id")
    user = auth_service.register_user_service(db, organization_id, payload.email, payload.password, payload.role_names)
    return UserResponse.from_orm(user)


@router.get("/me", response_model=UserResponse)
def get_current_user(
    authorization: Optional[str] = Header(None),
    x_organization_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    payload = parse_authorization_token(authorization)
    if x_organization_id and x_organization_id != payload.get("org_id"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization mismatch")

    user_id = payload.get("sub")
    user = auth_service.get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is inactive")

    return UserResponse.from_orm(user)


@router.post("/organizations/register", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
def register_organization(
    payload: OrganizationRegistrationRequest,
    db: Session = Depends(get_db),
):
    organization = auth_service.register_organization_service(db, payload.name, payload.admin_email, payload.admin_password)
    return OrganizationResponse.from_orm(organization)
