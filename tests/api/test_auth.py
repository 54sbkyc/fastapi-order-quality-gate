def test_register_user_success(client):
    response = client.post("/api/auth/register", json={"username": "alice", "password": "Passw0rd!"})

    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "alice"
    assert "id" in body


def test_login_success_returns_token(client, registered_user):
    response = client.post(
        "/api/auth/login",
        json={"username": registered_user["username"], "password": registered_user["password"]},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_wrong_password_returns_business_error(client, registered_user):
    response = client.post(
        "/api/auth/login",
        json={"username": registered_user["username"], "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json()["code"] == "INVALID_CREDENTIALS"


def test_protected_api_without_token_returns_unauthorized(client):
    response = client.get("/api/orders")

    assert response.status_code == 401
    assert response.json()["code"] == "NOT_AUTHENTICATED"

