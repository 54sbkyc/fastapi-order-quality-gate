from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.order import OrderCreate, OrderResponse
from app.services.order_service import (
    cancel_order,
    create_order,
    get_user_order,
    list_user_orders,
    pay_order,
)

router = APIRouter(prefix="/api/orders", tags=["订单接口"])
CurrentUser = Annotated[User, Depends(get_current_user)]
DbSession = Annotated[Session, Depends(get_db)]


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建订单",
    description="登录用户创建订单。创建成功后扣减商品库存，订单状态为 created。",
)
def create_new_order(
    payload: OrderCreate,
    current_user: CurrentUser,
    db: DbSession,
) -> OrderResponse:
    return create_order(db, current_user, payload)


@router.get(
    "",
    response_model=list[OrderResponse],
    summary="查询我的订单列表",
    description="只返回当前登录用户自己的订单，验证用户数据隔离。",
)
def list_orders(
    current_user: CurrentUser,
    db: DbSession,
) -> list[OrderResponse]:
    return list_user_orders(db, current_user)


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="查询订单详情",
    description="根据订单 ID 查询详情。用户不能访问其他人的订单。",
)
def get_order_detail(
    order_id: int,
    current_user: CurrentUser,
    db: DbSession,
) -> OrderResponse:
    return get_user_order(db, current_user, order_id)


@router.post(
    "/{order_id}/pay",
    response_model=OrderResponse,
    summary="支付订单",
    description="模拟支付订单。只有 created 状态的订单可以支付，支付后状态变为 paid。",
)
def pay_existing_order(
    order_id: int,
    current_user: CurrentUser,
    db: DbSession,
) -> OrderResponse:
    return pay_order(db, current_user, order_id)


@router.post(
    "/{order_id}/cancel",
    response_model=OrderResponse,
    summary="取消订单",
    description="取消 created 状态订单。取消成功后状态变为 cancelled，并恢复商品库存。",
)
def cancel_existing_order(
    order_id: int,
    current_user: CurrentUser,
    db: DbSession,
) -> OrderResponse:
    return cancel_order(db, current_user, order_id)
