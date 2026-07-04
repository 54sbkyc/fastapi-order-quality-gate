from decimal import Decimal

from app.models.order import Order
from tests.schemas.order_schema import OrderResponse


def test_create_order_success_decreases_stock_and_persists(
    client, auth_headers, seed_products, db_session
):
    product = seed_products[0]
    original_stock = product.stock

    response = client.post(
        "/api/orders",
        json={"product_id": product.id, "quantity": 2},
        headers=auth_headers,
    )

    assert response.status_code == 201
    body = OrderResponse.model_validate(response.json())
    assert body.product_id == product.id
    assert body.quantity == 2
    assert body.total_amount == product.price * Decimal("2")
    assert body.status == "created"

    db_session.refresh(product)
    db_order = db_session.get(Order, body.id)
    assert db_order is not None
    assert product.stock == original_stock - 2


def test_create_order_without_login_returns_unauthorized(client, seed_products):
    response = client.post(
        "/api/orders",
        json={"product_id": seed_products[0].id, "quantity": 1},
    )

    assert response.status_code == 401
    assert response.json()["code"] == "NOT_AUTHENTICATED"


def test_create_order_with_nonexistent_product_returns_business_error(client, auth_headers):
    response = client.post(
        "/api/orders",
        json={"product_id": 999999, "quantity": 1},
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["code"] == "PRODUCT_NOT_FOUND"


def test_create_order_with_insufficient_stock_returns_business_error(
    client, auth_headers, seed_products
):
    response = client.post(
        "/api/orders",
        json={"product_id": seed_products[0].id, "quantity": seed_products[0].stock + 1},
        headers=auth_headers,
    )

    assert response.status_code == 409
    assert response.json()["code"] == "INSUFFICIENT_STOCK"


def test_list_orders_only_returns_current_user_orders(
    client, auth_headers, another_auth_headers, seed_products
):
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

    response = client.get("/api/orders", headers=auth_headers)

    assert response.status_code == 200
    order_ids = [order["id"] for order in response.json()]
    assert order_ids == [own_order["id"]]


def test_user_cannot_access_another_users_order(
    client, auth_headers, another_auth_headers, seed_products
):
    own_order = client.post(
        "/api/orders",
        json={"product_id": seed_products[0].id, "quantity": 1},
        headers=auth_headers,
    ).json()

    response = client.get(f"/api/orders/{own_order['id']}", headers=another_auth_headers)

    assert response.status_code == 403
    assert response.json()["code"] == "FORBIDDEN_ORDER_ACCESS"

