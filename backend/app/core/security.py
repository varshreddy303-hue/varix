from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from .config import settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def _create_token(payload: Dict[str, Any], expires_delta: timedelta) -> str:
    to_encode = payload.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(user_id: str, organization_id: str, roles: Optional[list[str]] = None) -> str:
    return _create_token(
        {
            "sub": str(user_id),
            "org_id": str(organization_id),
            "roles": roles or [],
            "type": "access",
        },
        timedelta(minutes=settings.access_token_expire_minutes),
    )


def create_refresh_token(user_id: str, organization_id: str, refresh_version: int) -> str:
    return _create_token(
        {
            "sub": str(user_id),
            "org_id": str(organization_id),
            "type": "refresh",
            "version": refresh_version,
        },
        timedelta(days=settings.refresh_token_expire_days),
    )


def decode_jwt_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise JWTError("Token validation failed") from exc


def validate_token(token: str, expected_type: str = "access") -> Dict[str, Any]:
    payload = decode_jwt_token(token)
    token_type = payload.get("type")
    if token_type != expected_type:
        raise JWTError(f"Expected {expected_type} token, got {token_type}")
    return payload
