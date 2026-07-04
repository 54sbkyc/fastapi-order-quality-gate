import allure
import pytest

from app.models.order import Order


@allure.feature("Order API")
@allure.story("Order state transition")
@allure.title("Pay created order successfully")
def test_pay_created_order_success(client, auth_headers, created_order, db_session):
    with allure.step("Pay created order"):
        response = client.post(f"/api/orders/{created_order['id']}/pay", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["status"] == "paid"
    db_order = db_session.get(Order, created_order["id"])
    assert db_order.status == "paid"


@allure.feature("Order API")
@allure.story("Order state transition")
@allure.title("Cancel created order successfully and restore stock")
def test_cancel_created_order_success_restores_stock(
    client, auth_headers, created_order, seed_products, db_session
):
    product = seed_products[0]
    stock_after_create = product.stock

    with allure.step("Cancel created order"):
        response = client.post(f"/api/orders/{created_order['id']}/cancel", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"
    db_session.refresh(product)
    assert product.stock == stock_after_create + created_order["quantity"]


@allure.feature("Order API")
@allure.story("Order state transition")
@allure.title("Reject invalid order state transition")
@pytest.mark.parametrize(
    ("first_action", "second_action"),
    [
        pytest.param("pay", "cancel", id="paid-order-cannot-be-cancelled"),
        pytest.param("cancel", "pay", id="cancelled-order-cannot-be-paid"),
        pytest.param("pay", "pay", id="paid-order-cannot-be-paid-again"),
    ],
)
def test_invalid_order_state_transitions_return_business_error(
    client, auth_headers, created_order, first_action, second_action
):
    order_id = created_order["id"]

    with allure.step("Move order to first state"):
        first_response = client.post(f"/api/orders/{order_id}/{first_action}", headers=auth_headers)
    assert first_response.status_code == 200

    with allure.step("Try invalid second transition"):
        response = client.post(f"/api/orders/{order_id}/{second_action}", headers=auth_headers)

    assert response.status_code == 409
    assert response.json()["code"] == "INVALID_ORDER_STATE"
