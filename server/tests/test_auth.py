from datetime import timedelta

import pytest

from app.repositories import users as user_repository
from app.services.auth import create_access_token, hash_password


def assert_envelope(payload, success):
    assert payload["success"] is success
    assert set(payload) == {"success", "data", "message", "error_code"}


def register(client, username="alice", password="Password123", **extra):
    payload = {"username": username, "password": password, **extra}
    return client.post("/api/v1/auth/register", json=payload)


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def test_register_login_profile_password_and_logout_flow(client):
    response = register(client, nickname="Alice", contact="alice@example.com")
    payload = response.get_json()

    assert response.status_code == 201
    assert_envelope(payload, True)
    assert payload["data"]["token"]
    assert payload["data"]["user"]["username"] == "alice"
    assert payload["data"]["user"]["role"] == "user"
    assert payload["data"]["user"]["status"] == "active"
    token = payload["data"]["token"]

    me_response = client.get("/api/v1/users/me", headers=auth_header(token))
    assert me_response.status_code == 200
    assert me_response.get_json()["data"]["nickname"] == "Alice"

    update_response = client.put(
        "/api/v1/users/me",
        json={"nickname": "Alice Updated", "campus": "东校区"},
        headers=auth_header(token),
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["data"]["nickname"] == "Alice Updated"

    password_response = client.put(
        "/api/v1/auth/password",
        json={"current_password": "Password123", "new_password": "NewPassword123"},
        headers=auth_header(token),
    )
    assert password_response.status_code == 200

    old_login = client.post(
        "/api/v1/auth/login",
        json={"username": "alice", "password": "Password123"},
    )
    assert old_login.status_code == 401
    assert old_login.get_json()["error_code"] == "INVALID_CREDENTIALS"

    new_login = client.post(
        "/api/v1/auth/login",
        json={"username": "alice", "password": "NewPassword123"},
    )
    assert new_login.status_code == 200

    logout_response = client.post("/api/v1/auth/logout", headers=auth_header(token))
    assert logout_response.status_code == 200
    assert logout_response.get_json()["data"]["logged_out"] is True


def test_register_rejects_duplicate_username(client):
    assert register(client).status_code == 201
    response = register(client)
    payload = response.get_json()

    assert response.status_code == 409
    assert_envelope(payload, False)
    assert payload["error_code"] == "DUPLICATE_ACCOUNT"


def test_login_rejects_wrong_password(client):
    assert register(client).status_code == 201

    response = client.post(
        "/api/v1/auth/login",
        json={"username": "alice", "password": "wrong-password"},
    )
    payload = response.get_json()

    assert response.status_code == 401
    assert_envelope(payload, False)
    assert payload["error_code"] == "INVALID_CREDENTIALS"


def test_protected_endpoint_rejects_missing_and_expired_token(client, app):
    missing = client.get("/api/v1/users/me")
    assert missing.status_code == 401
    assert missing.get_json()["error_code"] == "AUTH_REQUIRED"

    with app.app_context():
        user = user_repository.create_user(
            "expired_user",
            hash_password("Password123"),
        )
        token, _expires_at = create_access_token(user, timedelta(seconds=-1))

    expired = client.get("/api/v1/users/me", headers=auth_header(token))
    assert expired.status_code == 401
    assert expired.get_json()["error_code"] == "TOKEN_EXPIRED"


def test_disabled_user_cannot_use_existing_token(client, app):
    response = register(client)
    token = response.get_json()["data"]["token"]
    user_id = response.get_json()["data"]["user"]["id"]

    with app.app_context():
        user_repository.set_user_status_for_tests(user_id, "disabled")
    disabled_response = client.get("/api/v1/users/me", headers=auth_header(token))

    assert disabled_response.status_code == 403
    assert disabled_response.get_json()["error_code"] == "USER_DISABLED"


@pytest.mark.parametrize("endpoint", ["/api/v1/auth/register", "/api/v1/users/me"])
def test_user_cannot_submit_permission_fields(client, endpoint):
    if endpoint.endswith("/register"):
        response = client.post(
            endpoint,
            json={
                "username": "mallory",
                "password": "Password123",
                "role": "admin",
            },
        )
    else:
        token = register(client).get_json()["data"]["token"]
        response = client.put(
            endpoint,
            json={"status": "disabled"},
            headers=auth_header(token),
        )

    assert response.status_code == 400
    assert response.get_json()["error_code"] == "VALIDATION_ERROR"
