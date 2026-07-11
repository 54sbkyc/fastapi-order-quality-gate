from datetime import UTC, datetime, timedelta

import allure
import jwt
import pytest

from app.core.config import settings


@allure.feature("Authentication API")
@allure.story("Register")
@allure.title("Register a new user successfully")
def test_register_user_success(client):
    with allure.step("Send register request"):
        response = client.post(
            "/api/auth/register",
            json={"username": "alice", "password": "Passw0rd!"},
        )

    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "alice"
    assert "id" in body


@allure.feature("Authentication API")
@allure.story("Register")
@allure.title("Reject duplicate username registration")
def test_register_duplicate_username_returns_business_error(client, registered_user):
    with allure.step("Register with an existing username"):
        response = client.post("/api/auth/register", json=registered_user)

    assert response.status_code == 409
    assert response.json()["code"] == "USER_ALREADY_EXISTS"


@allure.feature("Authentication API")
@allure.story("Login")
@allure.title("Login successfully and return JWT token")
def test_login_success_returns_token(client, registered_user):
    with allure.step("Login with valid credentials"):
        response = client.post(
            "/api/auth/login",
            json={"username": registered_user["username"], "password": registered_user["password"]},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


@allure.feature("Authentication API")
@allure.story("Login")
@allure.title("Reject invalid login credentials")
@pytest.mark.parametrize(
    "login_payload",
    [
        pytest.param({"username": "tester", "password": "wrong-password"}, id="wrong-password"),
        pytest.param({"username": "missing-user", "password": "Passw0rd!"}, id="unknown-user"),
    ],
)
def test_login_invalid_credentials_return_business_error(client, registered_user, login_payload):
    with allure.step("Login with invalid credentials"):
        response = client.post("/api/auth/login", json=login_payload)

    assert response.status_code == 401
    assert response.json()["code"] == "INVALID_CREDENTIALS"


@allure.feature("Authentication API")
@allure.story("Authorization")
@allure.title("Reject protected API access without token")
def test_protected_api_without_token_returns_unauthorized(client):
    with allure.step("Request protected API without Authorization header"):
        response = client.get("/api/orders")

    assert response.status_code == 401
    assert response.json()["code"] == "NOT_AUTHENTICATED"


@allure.feature("Authentication API")
@allure.story("Authorization")
@allure.title("Reject malformed or forged Bearer tokens")
@pytest.mark.parametrize(
    "token",
    [
        pytest.param("not-a-jwt-token", id="malformed-token"),
        pytest.param(
            jwt.encode(
                {"sub": "1", "exp": datetime.now(UTC) + timedelta(minutes=5)},
                "wrong-secret-with-at-least-32-bytes",
                algorithm=settings.jwt_algorithm,
            ),
            id="forged-signature",
        ),
    ],
)
def test_protected_api_with_invalid_token_returns_invalid_token(client, token):
    with allure.step("Request protected API with invalid token"):
        response = client.get("/api/orders", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    assert response.json()["code"] == "INVALID_TOKEN"


@allure.feature("Authentication API")
@allure.story("Authorization")
@allure.title("Reject expired JWT token")
def test_protected_api_with_expired_token_returns_invalid_token(client):
    expired_token = jwt.encode(
        {"sub": "1", "exp": datetime.now(UTC) - timedelta(minutes=1)},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    with allure.step("Request protected API with expired token"):
        response = client.get("/api/orders", headers={"Authorization": f"Bearer {expired_token}"})

    assert response.status_code == 401
    assert response.json()["code"] == "INVALID_TOKEN"


@allure.feature("Authentication API")
@allure.story("Authorization")
@allure.title("Reject valid token when user no longer exists")
def test_protected_api_with_nonexistent_user_token_returns_invalid_token(client):
    token_for_missing_user = jwt.encode(
        {"sub": "999999", "exp": datetime.now(UTC) + timedelta(minutes=5)},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    with allure.step("Request protected API with token for nonexistent user"):
        response = client.get(
            "/api/orders",
            headers={"Authorization": f"Bearer {token_for_missing_user}"},
        )

    assert response.status_code == 401
    assert response.json()["code"] == "INVALID_TOKEN"
