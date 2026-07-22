from decimal import Decimal

import allure
import pytest
from sqlalchemy import select

from app.models.order import Order
from app.models.order_idempotency import OrderIdempotencyRecord
from tests.schemas.order_schema import OrderResponse


@allure.feature("Order API")
@allure.story("Order creation")
@allure.title("Create order successfully and verify database side effects")
def test_create_order_success_decreases_stock_and_persists(
    client, auth_headers, seed_products, db_session
):
    product = seed_products[0]
    original_stock = product.stock

    with allure.step("Create order through API"):
        response = client.post(
            "/api/orders",
            json={"product_id": product.id, "quantity": 2},
            headers=auth_headers,
        )

    assert response.status_code == 201
    assert response.headers["Idempotency-Replayed"] == "false"
    body = OrderResponse.model_validate(response.json())
    assert body.product_id == product.id
    assert body.quantity == 2
    assert body.total_amount == product.price * Decimal("2")
    assert body.status == "created"

    db_session.refresh(product)
    db_order = db_session.get(Order, body.id)
    assert db_order is not None
    assert product.stock == original_stock - 2


@allure.feature("Order API")
@allure.story("Order idempotency")
@allure.title("Replay the same order request without duplicating order or stock deduction")
def test_create_order_replay_returns_same_order_without_duplicate_side_effects(
    client, auth_headers, seed_products, db_session
):
    product = seed_products[0]
    original_stock = product.stock
    headers = {**auth_headers, "Idempotency-Key": "order-retry-0001"}
    payload = {"product_id": product.id, "quantity": 2}

    with allure.step("Send the same idempotent order request twice"):
        first_response = client.post("/api/orders", json=payload, headers=headers)
        replay_response = client.post("/api/orders", json=payload, headers=headers)

    assert first_response.status_code == 201
    assert first_response.headers["Idempotency-Replayed"] == "false"
    assert replay_response.status_code == 200
    assert replay_response.headers["Idempotency-Replayed"] == "true"
    assert replay_response.json() == first_response.json()

    db_session.refresh(product)
    orders = db_session.scalars(select(Order)).all()
    records = db_session.scalars(select(OrderIdempotencyRecord)).all()
    assert len(orders) == 1
    assert len(records) == 1
    assert records[0].order_id == orders[0].id
    assert product.stock == original_stock - 2


@allure.feature("Order API")
@allure.story("Order idempotency")
@allure.title("Reject reusing an idempotency key for different order parameters")
def test_create_order_rejects_idempotency_key_payload_conflict(
    client, auth_headers, seed_products, db_session
):
    product = seed_products[0]
    original_stock = product.stock
    headers = {**auth_headers, "Idempotency-Key": "order-conflict-0001"}

    first_response = client.post(
        "/api/orders",
        json={"product_id": product.id, "quantity": 1},
        headers=headers,
    )
    conflict_response = client.post(
        "/api/orders",
        json={"product_id": product.id, "quantity": 2},
        headers=headers,
    )

    assert first_response.status_code == 201
    assert conflict_response.status_code == 409
    assert conflict_response.json()["code"] == "IDEMPOTENCY_KEY_CONFLICT"

    db_session.refresh(product)
    assert len(db_session.scalars(select(Order)).all()) == 1
    assert product.stock == original_stock - 1


@allure.feature("Order API")
@allure.story("Order idempotency")
@allure.title("Scope the same idempotency key independently for each user")
def test_create_order_idempotency_key_is_scoped_by_user(
    client, auth_headers, another_auth_headers, seed_products, db_session
):
    product = seed_products[0]
    headers = {"Idempotency-Key": "shared-user-key-0001"}
    payload = {"product_id": product.id, "quantity": 1}

    first_response = client.post(
        "/api/orders",
        json=payload,
        headers={**auth_headers, **headers},
    )
    second_response = client.post(
        "/api/orders",
        json=payload,
        headers={**another_auth_headers, **headers},
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201
    assert first_response.json()["id"] != second_response.json()["id"]
    records = db_session.scalars(select(OrderIdempotencyRecord)).all()
    assert len(records) == 2
    assert {record.user_id for record in records} == {
        first_response.json()["user_id"],
        second_response.json()["user_id"],
    }


@allure.feature("Order API")
@allure.story("Order idempotency")
@allure.title("Reject invalid idempotency key format")
@pytest.mark.parametrize(
    "idempotency_key",
    [
        pytest.param("short", id="too-short"),
        pytest.param("contains spaces", id="invalid-character"),
    ],
)
def test_create_order_rejects_invalid_idempotency_key(
    client, auth_headers, seed_products, idempotency_key
):
    response = client.post(
        "/api/orders",
        json={"product_id": seed_products[0].id, "quantity": 1},
        headers={**auth_headers, "Idempotency-Key": idempotency_key},
    )

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"


@allure.feature("Order API")
@allure.story("Order authorization")
@allure.title("Reject order creation without login")
def test_create_order_without_login_returns_unauthorized(client, seed_products):
    with allure.step("Create order without Authorization header"):
        response = client.post(
            "/api/orders",
            json={"product_id": seed_products[0].id, "quantity": 1},
        )

    assert response.status_code == 401
    assert response.json()["code"] == "NOT_AUTHENTICATED"


@allure.feature("Order API")
@allure.story("Order validation")
@allure.title("Reject nonexistent product when creating order")
def test_create_order_with_nonexistent_product_returns_business_error(client, auth_headers):
    with allure.step("Create order with missing product id"):
        response = client.post(
            "/api/orders",
            json={"product_id": 999999, "quantity": 1},
            headers=auth_headers,
        )

    assert response.status_code == 404
    assert response.json()["code"] == "PRODUCT_NOT_FOUND"


@allure.feature("Order API")
@allure.story("Order validation")
@allure.title("Reject order when stock is insufficient")
def test_create_order_with_insufficient_stock_returns_business_error(
    client, auth_headers, seed_products
):
    with allure.step("Create order with quantity greater than stock"):
        response = client.post(
            "/api/orders",
            json={"product_id": seed_products[0].id, "quantity": seed_products[0].stock + 1},
            headers=auth_headers,
        )

    assert response.status_code == 409
    assert response.json()["code"] == "INSUFFICIENT_STOCK"


@allure.feature("Order API")
@allure.story("Order validation")
@allure.title("Reject order creation for inactive product")
def test_create_order_with_inactive_product_returns_business_error(
    client, auth_headers, seed_products, db_session
):
    product = seed_products[0]
    product.is_active = False
    db_session.commit()

    with allure.step("Create order for an inactive product"):
        response = client.post(
            "/api/orders",
            json={"product_id": product.id, "quantity": 1},
            headers=auth_headers,
        )

    assert response.status_code == 409
    assert response.json()["code"] == "PRODUCT_INACTIVE"


@allure.feature("Order API")
@allure.story("Order validation")
@allure.title("Reject invalid order quantity")
@pytest.mark.parametrize(
    "quantity",
    [
        pytest.param(0, id="zero"),
        pytest.param(-1, id="negative"),
        pytest.param(101, id="over-limit"),
    ],
)
def test_create_order_with_invalid_quantity_returns_validation_error(
    client, auth_headers, seed_products, quantity
):
    with allure.step("Create order with invalid quantity"):
        response = client.post(
            "/api/orders",
            json={"product_id": seed_products[0].id, "quantity": quantity},
            headers=auth_headers,
        )

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"


@allure.feature("Order API")
@allure.story("Order query")
@allure.title("List orders only returns current user's orders")
def test_list_orders_only_returns_current_user_orders(
    client, auth_headers, another_auth_headers, seed_products
):
    with allure.step("Create one order for current user and one order for another user"):
        own_order = client.post(
            "/api/orders",
            json={"product_id": seed_products[0].id, "quantity": 1},
            headers=auth_headers,
        ).json()
        client.post(
            "/api/orders",
            json={"product_id": seed_products[1].id, "quantity": 1},
            headers=another_auth_headers,
        )

    with allure.step("Query current user's order list"):
        response = client.get("/api/orders", headers=auth_headers)

    assert response.status_code == 200
    order_ids = [order["id"] for order in response.json()]
    assert order_ids == [own_order["id"]]


@allure.feature("Order API")
@allure.story("Order authorization")
@allure.title("Reject access to another user's order")
def test_user_cannot_access_another_users_order(
    client, auth_headers, another_auth_headers, seed_products
):
    with allure.step("Create order for current user"):
        own_order = client.post(
            "/api/orders",
            json={"product_id": seed_products[0].id, "quantity": 1},
            headers=auth_headers,
        ).json()

    with allure.step("Query order with another user's token"):
        response = client.get(f"/api/orders/{own_order['id']}", headers=another_auth_headers)

    assert response.status_code == 403
    assert response.json()["code"] == "FORBIDDEN_ORDER_ACCESS"
