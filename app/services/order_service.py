from dataclasses import dataclass

from fastapi import status
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessException
from app.models.order import (
    ORDER_STATUS_CANCELLED,
    ORDER_STATUS_CREATED,
    ORDER_STATUS_PAID,
    Order,
)
from app.models.order_idempotency import OrderIdempotencyRecord
from app.models.product import Product
from app.models.user import User
from app.schemas.order import OrderCreate


@dataclass(frozen=True)
class OrderCreationResult:
    order: Order
    replayed: bool


def list_user_orders(db: Session, user: User) -> list[Order]:
    return list(db.scalars(select(Order).where(Order.user_id == user.id).order_by(Order.id)).all())


def get_user_order(db: Session, user: User, order_id: int) -> Order:
    order = db.get(Order, order_id)
    if order is None:
        raise BusinessException("ORDER_NOT_FOUND", "订单不存在", status.HTTP_404_NOT_FOUND)
    if order.user_id != user.id:
        raise BusinessException(
            "FORBIDDEN_ORDER_ACCESS",
            "不能访问其他用户的订单",
            status.HTTP_403_FORBIDDEN,
        )
    return order


def _get_idempotency_record(
    db: Session,
    user_id: int,
    idempotency_key: str,
) -> OrderIdempotencyRecord | None:
    return db.scalar(
        select(OrderIdempotencyRecord).where(
            OrderIdempotencyRecord.user_id == user_id,
            OrderIdempotencyRecord.idempotency_key == idempotency_key,
        )
    )


def _resolve_idempotent_replay(
    db: Session,
    record: OrderIdempotencyRecord,
    payload: OrderCreate,
) -> OrderCreationResult:
    if record.product_id != payload.product_id or record.quantity != payload.quantity:
        raise BusinessException(
            "IDEMPOTENCY_KEY_CONFLICT",
            "同一个 Idempotency-Key 不能用于不同的下单参数",
            status.HTTP_409_CONFLICT,
        )

    order = db.get(Order, record.order_id)
    if order is None:
        raise BusinessException(
            "IDEMPOTENCY_RECORD_INVALID",
            "幂等记录关联的订单不存在",
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    return OrderCreationResult(order=order, replayed=True)


def create_order_with_idempotency(
    db: Session,
    user: User,
    payload: OrderCreate,
    idempotency_key: str | None,
) -> OrderCreationResult:
    user_id = user.id
    if idempotency_key is not None:
        existing_record = _get_idempotency_record(db, user_id, idempotency_key)
        if existing_record is not None:
            return _resolve_idempotent_replay(db, existing_record, payload)

    product = db.get(Product, payload.product_id)
    if product is None:
        raise BusinessException("PRODUCT_NOT_FOUND", "商品不存在", status.HTTP_404_NOT_FOUND)
    if not product.is_active:
        raise BusinessException("PRODUCT_INACTIVE", "商品已下架", status.HTTP_409_CONFLICT)
    stock_update = (
        update(Product)
        .where(Product.id == product.id, Product.stock >= payload.quantity)
        .values(stock=Product.stock - payload.quantity)
        .execution_options(synchronize_session=False)
    )
    result = db.execute(stock_update)
    if result.rowcount != 1:
        db.rollback()
        raise BusinessException(
            "INSUFFICIENT_STOCK",
            "商品库存不足",
            status.HTTP_409_CONFLICT,
        )

    db.refresh(product)
    order = Order(
        user_id=user_id,
        product_id=product.id,
        quantity=payload.quantity,
        total_amount=product.price * payload.quantity,
        status=ORDER_STATUS_CREATED,
    )
    try:
        db.add(order)
        db.flush()
        if idempotency_key is not None:
            db.add(
                OrderIdempotencyRecord(
                    user_id=user_id,
                    idempotency_key=idempotency_key,
                    order_id=order.id,
                    product_id=payload.product_id,
                    quantity=payload.quantity,
                )
            )
        db.commit()
    except IntegrityError:
        db.rollback()
        if idempotency_key is not None:
            existing_record = _get_idempotency_record(db, user_id, idempotency_key)
            if existing_record is not None:
                return _resolve_idempotent_replay(db, existing_record, payload)
        raise

    db.refresh(order)
    return OrderCreationResult(order=order, replayed=False)


def create_order(db: Session, user: User, payload: OrderCreate) -> Order:
    return create_order_with_idempotency(db, user, payload, None).order


def pay_order(db: Session, user: User, order_id: int) -> Order:
    order = get_user_order(db, user, order_id)
    transition = db.execute(
        update(Order)
        .where(
            Order.id == order.id,
            Order.user_id == user.id,
            Order.status == ORDER_STATUS_CREATED,
        )
        .values(status=ORDER_STATUS_PAID)
        .execution_options(synchronize_session=False)
    )
    if transition.rowcount != 1:
        db.rollback()
        raise BusinessException(
            "INVALID_ORDER_STATE",
            "只有 created 状态的订单可以支付",
            status.HTTP_409_CONFLICT,
        )

    db.commit()
    db.refresh(order)
    return order


def cancel_order(db: Session, user: User, order_id: int) -> Order:
    order = get_user_order(db, user, order_id)
    transition = db.execute(
        update(Order)
        .where(
            Order.id == order.id,
            Order.user_id == user.id,
            Order.status == ORDER_STATUS_CREATED,
        )
        .values(status=ORDER_STATUS_CANCELLED)
        .execution_options(synchronize_session=False)
    )
    if transition.rowcount != 1:
        db.rollback()
        raise BusinessException(
            "INVALID_ORDER_STATE",
            "只有 created 状态的订单可以取消",
            status.HTTP_409_CONFLICT,
        )

    stock_restore = db.execute(
        update(Product)
        .where(Product.id == order.product_id)
        .values(stock=Product.stock + order.quantity)
        .execution_options(synchronize_session=False)
    )
    if stock_restore.rowcount != 1:
        db.rollback()
        raise BusinessException(
            "PRODUCT_NOT_FOUND",
            "商品不存在",
            status.HTTP_404_NOT_FOUND,
        )

    db.commit()
    db.refresh(order)
    return order
