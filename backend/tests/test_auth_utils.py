from uuid import uuid4

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    validate_token,
    verify_password,
)


def test_password_hashing_and_verification():
    raw_password = "StrongPass123!"
    hashed = hash_password(raw_password)

    assert verify_password(raw_password, hashed)
    assert not verify_password("WrongPassword", hashed)


def test_jwt_access_and_refresh_token_roundtrip():
    user_id = str(uuid4())
    organization_id = str(uuid4())
    access_token = create_access_token(user_id, organization_id, ["admin", "member"])
    refresh_token = create_refresh_token(user_id, organization_id, 0)

    access_payload = validate_token(access_token, expected_type="access")
    refresh_payload = validate_token(refresh_token, expected_type="refresh")

    assert access_payload["sub"] == user_id
    assert access_payload["org_id"] == organization_id
    assert "admin" in access_payload["roles"]
    assert refresh_payload["sub"] == user_id
    assert refresh_payload["org_id"] == organization_id
    assert refresh_payload["version"] == 0
