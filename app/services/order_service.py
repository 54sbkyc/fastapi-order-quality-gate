from fastapi import status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessException
from app.models.order import (
    ORDER_STATUS_CANCELLED,
    ORDER_STATUS_CREATED,
    ORDER_STATUS_PAID,
    Order,
)
from app.models.product import Product
from app.models.user import User
from app.schemas.order import OrderCreate


def list_user_orders(db: Session, user: User) -> list[Order]:
    return list(db.scalars(select(Order).where(Order.user_id == user.id).order_by(Order.id)).all())


def get_user_order(db: Session, user: User, order_id: int) -> Order:
    order = db.get(Order, order_id)
    if order is None:
        raise BusinessException("ORDER_NOT_FOUND", "Order not found", status.HTTP_404_NOT_FOUND)
    if order.user_id != user.id:
        raise BusinessException(
            "FORBIDDEN_ORDER_ACCESS",
            "Cannot access another user's order",
            status.HTTP_403_FORBIDDEN,
        )
    return order


def create_order(db: Session, user: User, payload: OrderCreate) -> Order:
    product = db.get(Product, payload.product_id)
    if product is None:
        raise BusinessException("PRODUCT_NOT_FOUND", "Product not found", status.HTTP_404_NOT_FOUND)
    if not product.is_active:
        raise BusinessException("PRODUCT_INACTIVE", "Product is inactive", status.HTTP_409_CONFLICT)
    if product.stock < payload.quantity:
        raise BusinessException(
            "INSUFFICIENT_STOCK",
            "Insufficient product stock",
            status.HTTP_409_CONFLICT,
        )

    product.stock -= payload.quantity
    order = Order(
        user_id=user.id,
        product_id=product.id,
        quantity=payload.quantity,
        total_amount=product.price * payload.quantity,
        status=ORDER_STATUS_CREATED,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def pay_order(db: Session, user: User, order_id: int) -> Order:
    order = get_user_order(db, user, order_id)
    if order.status != ORDER_STATUS_CREATED:
        raise BusinessException(
            "INVALID_ORDER_STATE",
            "Only created orders can be paid",
            status.HTTP_409_CONFLICT,
        )

    order.status = ORDER_STATUS_PAID
    db.commit()
    db.refresh(order)
    return order


def cancel_order(db: Session, user: User, order_id: int) -> Order:
    order = get_user_order(db, user, order_id)
    if order.status != ORDER_STATUS_CREATED:
        raise BusinessException(
            "INVALID_ORDER_STATE",
            "Only created orders can be cancelled",
            status.HTTP_409_CONFLICT,
        )

    product = db.get(Product, order.product_id)
    if product is not None:
        product.stock += order.quantity
    order.status = ORDER_STATUS_CANCELLED
    db.commit()
    db.refresh(order)
    return order

