import pytest
from fastapi import HTTPException
from app.services import auth_service
from app.core.security import hash_password


class DummyUser:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.roles = kwargs.get("roles", [])


class DummyRole:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture(autouse=True)
def clear_patches(monkeypatch):
    yield


def test_register_organization_service_creates_organization_and_admin(monkeypatch):
    created_org = None
    created_role = None
    created_user = None

    def fake_get_organization_by_name(db, name):
        return None

    def fake_create_organization(db, organization):
        organization.id = "org-123"
        return organization

    def fake_get_role_by_name(db, organization_id, role_name):
        return None

    def fake_create_role(db, role):
        role.id = 1
        return role

    def fake_create_user(db, user):
        user.id = "user-123"
        return user

    def fake_add_role_to_user(db, user, role):
        user.roles.append(role)
        return user

    monkeypatch.setattr(auth_service, "get_organization_by_name", fake_get_organization_by_name)
    monkeypatch.setattr(auth_service, "create_organization", fake_create_organization)
    monkeypatch.setattr(auth_service, "get_role_by_name", fake_get_role_by_name)
    monkeypatch.setattr(auth_service, "create_role", fake_create_role)
    monkeypatch.setattr(auth_service, "create_user", fake_create_user)
    monkeypatch.setattr(auth_service, "add_role_to_user", fake_add_role_to_user)

    organization = auth_service.register_organization_service(None, "Acme Co", "admin@acme.test", "SecurePass123")

    assert organization.id == "org-123"
    assert organization.name == "Acme Co"


def test_authenticate_user_service_validates_credentials(monkeypatch):
    dummy_user = DummyUser(
        id="user-abc",
        organization_id="org-123",
        hashed_password=hash_password("Secret123!"),
        is_active=True,
        refresh_token_version=0,
        roles=[DummyRole(name="member")],
    )

    def fake_get_user_by_email(db, email, organization_id=None):
        return dummy_user

    monkeypatch.setattr(auth_service, "get_user_by_email", fake_get_user_by_email)

    tokens = auth_service.authenticate_user_service(None, "org-123", "user@example.com", "Secret123!")

    assert "access_token" in tokens
    assert "refresh_token" in tokens


def test_authenticate_user_service_allows_login_without_organization_id(monkeypatch):
    dummy_user = DummyUser(
        id="user-abc",
        organization_id="org-123",
        hashed_password=hash_password("Secret123!"),
        is_active=True,
        refresh_token_version=0,
        roles=[DummyRole(name="member")],
    )

    def fake_get_users_by_email(db, email):
        return [dummy_user]

    def fake_get_user_by_email(db, email, organization_id=None):
        return None

    monkeypatch.setattr(auth_service, "get_users_by_email", fake_get_users_by_email)
    monkeypatch.setattr(auth_service, "get_user_by_email", fake_get_user_by_email)

    tokens = auth_service.authenticate_user_service(None, None, "user@example.com", "Secret123!")

    assert "access_token" in tokens
    assert "refresh_token" in tokens


def test_authenticate_user_service_rejects_bad_password(monkeypatch):
    dummy_user = DummyUser(
        id="user-abc",
        organization_id="org-123",
        hashed_password=hash_password("Secret123!"),
        is_active=True,
        refresh_token_version=0,
        roles=[DummyRole(name="member")],
    )

    def fake_get_user_by_email(db, email, organization_id=None):
        return dummy_user

    monkeypatch.setattr(auth_service, "get_user_by_email", fake_get_user_by_email)

    with pytest.raises(Exception):
        auth_service.authenticate_user_service(None, "org-123", "user@example.com", "WrongPassword")
