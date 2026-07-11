from decimal import Decimal

import allure
import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.core.exceptions import BusinessException
from app.models.order import Order
from app.models.product import Product
from app.models.user import User
from app.schemas.order import OrderCreate
from app.services.order_service import cancel_order, create_order


@allure.feature("Order API")
@allure.story("Inventory consistency")
@allure.title("Reject stale-session order when last stock has already been sold")
def test_stale_inventory_session_cannot_create_second_order(db_session: Session):
    product = Product(
        name="Limited Keyboard",
        price=Decimal("199.00"),
        stock=1,
        is_active=True,
    )
    first_user = User(username="stock-user-a", password_hash="test-hash")
    second_user = User(username="stock-user-b", password_hash="test-hash")
    db_session.add_all([product, first_user, second_user])
    db_session.commit()
    db_session.refresh(product)
    db_session.refresh(first_user)
    db_session.refresh(second_user)

    SessionLocal = sessionmaker(bind=db_session.get_bind(), autocommit=False, autoflush=False)

    first_session = SessionLocal()
    second_session = SessionLocal()
    try:
        first_stale_product = first_session.get(Product, product.id)
        second_stale_product = second_session.get(Product, product.id)
        assert first_stale_product.stock == 1
        assert second_stale_product.stock == 1

        first_order = create_order(
            first_session,
            first_session.get(User, first_user.id),
            OrderCreate(product_id=product.id, quantity=1),
        )

        with pytest.raises(BusinessException) as exc_info:
            create_order(
                second_session,
                second_session.get(User, second_user.id),
                OrderCreate(product_id=product.id, quantity=1),
            )

        assert first_order.id is not None
        assert exc_info.value.code == "INSUFFICIENT_STOCK"
    finally:
        first_session.close()
        second_session.close()

    db_session.expire_all()
    final_product = db_session.get(Product, product.id)
    orders = db_session.scalars(select(Order).where(Order.product_id == product.id)).all()

    assert final_product.stock == 0
    assert len(orders) == 1


@allure.feature("Order API")
@allure.story("Order state consistency")
@allure.title("Concurrent cancellation restores inventory only once")
def test_stale_order_session_cannot_restore_stock_twice(db_session: Session):
    product = Product(
        name="Cancellation Keyboard",
        price=Decimal("299.00"),
        stock=2,
        is_active=True,
    )
    user = User(username="cancel-user", password_hash="test-hash")
    db_session.add_all([product, user])
    db_session.commit()
    db_session.refresh(product)
    db_session.refresh(user)

    order = create_order(
        db_session,
        user,
        OrderCreate(product_id=product.id, quantity=1),
    )
    SessionLocal = sessionmaker(bind=db_session.get_bind(), autocommit=False, autoflush=False)
    first_session = SessionLocal()
    second_session = SessionLocal()
    try:
        first_order = first_session.get(Order, order.id)
        second_order = second_session.get(Order, order.id)
        assert first_order.status == "created"
        assert second_order.status == "created"

        cancelled_order = cancel_order(
            first_session,
            first_session.get(User, user.id),
            order.id,
        )

        with pytest.raises(BusinessException) as exc_info:
            cancel_order(
                second_session,
                second_session.get(User, user.id),
                order.id,
            )

        assert cancelled_order.status == "cancelled"
        assert exc_info.value.code == "INVALID_ORDER_STATE"
    finally:
        first_session.close()
        second_session.close()

    db_session.expire_all()
    final_product = db_session.get(Product, product.id)
    final_order = db_session.get(Order, order.id)

    assert final_product.stock == 2
    assert final_order.status == "cancelled"
