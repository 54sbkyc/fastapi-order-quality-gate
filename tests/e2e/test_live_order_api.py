from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

import allure
import pytest

from tests.e2e.client import OrderApiClient
from tests.schemas.auth_schema import ErrorResponse, TokenResponse, UserResponse
from tests.schemas.order_schema import OrderResponse
from tests.schemas.product_schema import ProductResponse

PASSWORD = "Passw0rd!"


def _new_username(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:12]}"


def _register_and_login(api: OrderApiClient, prefix: str) -> str:
    username = _new_username(prefix)
    register_response = api.register(username, PASSWORD)
    assert register_response.status_code == 201
    registered_user = UserResponse.model_validate(register_response.json())
    assert registered_user.username == username

    login_response = api.login(username, PASSWORD)
    assert login_response.status_code == 200
    token = TokenResponse.model_validate(login_response.json())
    assert token.token_type == "bearer"
    return token.access_token


@allure.feature("Live API E2E")
@allure.story("Order lifecycle")
@allure.title("Running service supports the complete order lifecycle over HTTP")
@pytest.mark.e2e
@pytest.mark.smoke
def test_live_order_lifecycle_over_http(live_api: OrderApiClient):
    health_body = live_api.health().json()
    assert health_body["status"] == "ok"

    token = _register_and_login(live_api, "e2e-smoke")
    products_response = live_api.list_products()
    assert products_response.status_code == 200
    products = [ProductResponse.model_validate(item) for item in products_response.json()]
    product = next((item for item in products if item.is_active and item.stock > 0), None)
    assert product is not None, "测试环境没有可下单的在售库存"
    original_stock = product.stock

    order_id: int | None = None
    cancelled = False
    try:
        create_response = live_api.create_order(token, product.id, 1)
        assert create_response.status_code == 201
        order = OrderResponse.model_validate(create_response.json())
        order_id = order.id
        assert order.status == "created"
        assert order.total_amount == product.price * Decimal("1")

        detail_response = live_api.get_order(token, order.id)
        assert detail_response.status_code == 200
        assert OrderResponse.model_validate(detail_response.json()).id == order.id

        cancel_response = live_api.cancel_order(token, order.id)
        assert cancel_response.status_code == 200
        assert OrderResponse.model_validate(cancel_response.json()).status == "cancelled"
        cancelled = True

        product_response = live_api.get_product(product.id)
        assert product_response.status_code == 200
        restored_product = ProductResponse.model_validate(product_response.json())
        assert restored_product.stock == original_stock
        transcript = live_api.dump_history()
        assert PASSWORD not in transcript
        assert token not in transcript
    finally:
        if order_id is not None and not cancelled:
            live_api.cancel_order(token, order_id)


@allure.feature("Live API E2E")
@allure.story("Order idempotency")
@allure.title("Running service prevents duplicate orders when a client retries over HTTP")
@pytest.mark.e2e
@pytest.mark.regression
def test_live_api_prevents_duplicate_order_retry(live_api: OrderApiClient):
    token = _register_and_login(live_api, "e2e-idempotency")
    products = [
        ProductResponse.model_validate(item) for item in live_api.list_products().json()
    ]
    product = next((item for item in products if item.is_active and item.stock > 0), None)
    assert product is not None, "测试环境没有可下单的在售库存"
    idempotency_key = f"e2e-order-{uuid4().hex}"

    first_response = live_api.create_order(
        token,
        product.id,
        1,
        idempotency_key=idempotency_key,
    )
    assert first_response.status_code == 201
    first_order = OrderResponse.model_validate(first_response.json())
    try:
        replay_response = live_api.create_order(
            token,
            product.id,
            1,
            idempotency_key=idempotency_key,
        )
        assert replay_response.status_code == 200
        assert replay_response.headers["Idempotency-Replayed"] == "true"
        assert OrderResponse.model_validate(replay_response.json()).id == first_order.id

        orders = [
            OrderResponse.model_validate(item) for item in live_api.list_orders(token).json()
        ]
        assert [order.id for order in orders] == [first_order.id]

        current_product = ProductResponse.model_validate(
            live_api.get_product(product.id).json()
        )
        assert current_product.stock == product.stock - 1
    finally:
        cleanup_response = live_api.cancel_order(token, first_order.id)
        assert cleanup_response.status_code == 200


@allure.feature("Live API E2E")
@allure.story("Authentication")
@allure.title("Running service rejects an invalid bearer token")
@pytest.mark.e2e
@pytest.mark.regression
def test_live_api_rejects_invalid_token(live_api: OrderApiClient):
    response = live_api.list_orders("invalid-e2e-token")

    assert response.status_code == 401
    error = ErrorResponse.model_validate(response.json())
    assert error.code == "INVALID_TOKEN"


@allure.feature("Live API E2E")
@allure.story("Authorization")
@allure.title("Running service isolates orders between real HTTP users")
@pytest.mark.e2e
@pytest.mark.regression
def test_live_api_enforces_user_order_isolation(live_api: OrderApiClient):
    owner_token = _register_and_login(live_api, "e2e-owner")
    other_token = _register_and_login(live_api, "e2e-other")
    products = [
        ProductResponse.model_validate(item) for item in live_api.list_products().json()
    ]
    product = next((item for item in products if item.is_active and item.stock > 0), None)
    assert product is not None, "测试环境没有可下单的在售库存"

    create_response = live_api.create_order(owner_token, product.id, 1)
    assert create_response.status_code == 201
    order = OrderResponse.model_validate(create_response.json())
    try:
        forbidden_response = live_api.get_order(other_token, order.id)
        assert forbidden_response.status_code == 403
        error = ErrorResponse.model_validate(forbidden_response.json())
        assert error.code == "FORBIDDEN_ORDER_ACCESS"
    finally:
        cleanup_response = live_api.cancel_order(owner_token, order.id)
        assert cleanup_response.status_code == 200
