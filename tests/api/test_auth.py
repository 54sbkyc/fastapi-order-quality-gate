import allure
import pytest


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
