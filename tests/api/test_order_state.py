from app.models.order import Order


def test_pay_created_order_success(client, auth_headers, created_order, db_session):
    response = client.post(f"/api/orders/{created_order['id']}/pay", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["status"] == "paid"
    db_order = db_session.get(Order, created_order["id"])
    assert db_order.status == "paid"


def test_cancel_created_order_success_restores_stock(
    client, auth_headers, created_order, seed_products, db_session
):
    product = seed_products[0]
    stock_after_create = product.stock

    response = client.post(f"/api/orders/{created_order['id']}/cancel", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"
    db_session.refresh(product)
    assert product.stock == stock_after_create + created_order["quantity"]


def test_paid_order_cannot_be_cancelled(client, auth_headers, created_order):
    pay_response = client.post(f"/api/orders/{created_order['id']}/pay", headers=auth_headers)
    assert pay_response.status_code == 200

    response = client.post(f"/api/orders/{created_order['id']}/cancel", headers=auth_headers)

    assert response.status_code == 409
    assert response.json()["code"] == "INVALID_ORDER_STATE"


def test_cancelled_order_cannot_be_paid(client, auth_headers, created_order):
    cancel_response = client.post(f"/api/orders/{created_order['id']}/cancel", headers=auth_headers)
    assert cancel_response.status_code == 200

    response = client.post(f"/api/orders/{created_order['id']}/pay", headers=auth_headers)

    assert response.status_code == 409
    assert response.json()["code"] == "INVALID_ORDER_STATE"


def test_paying_same_order_twice_returns_business_error(client, auth_headers, created_order):
    first_response = client.post(f"/api/orders/{created_order['id']}/pay", headers=auth_headers)
    assert first_response.status_code == 200

    response = client.post(f"/api/orders/{created_order['id']}/pay", headers=auth_headers)

    assert response.status_code == 409
    assert response.json()["code"] == "INVALID_ORDER_STATE"

