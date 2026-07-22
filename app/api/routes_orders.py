from typing import Annotated

from fastapi import APIRouter, Depends, Header, Response, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.error import ErrorResponse
from app.schemas.order import OrderCreate, OrderResponse
from app.services.order_service import (
    cancel_order,
    create_order_with_idempotency,
    get_user_order,
    list_user_orders,
    pay_order,
)

router = APIRouter(prefix="/api/orders", tags=["订单接口"])
CurrentUser = Annotated[User, Depends(get_current_user)]
DbSession = Annotated[Session, Depends(get_db)]
IdempotencyKey = Annotated[
    str | None,
    Header(
        alias="Idempotency-Key",
        min_length=8,
        max_length=64,
        pattern=r"^[A-Za-z0-9._:-]+$",
    ),
]

AUTH_RESPONSE = {401: {"model": ErrorResponse, "description": "未登录或 token 无效"}}
VALIDATION_RESPONSE = {422: {"model": ErrorResponse, "description": "请求参数校验失败"}}


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建订单",
    description=(
        "登录用户创建订单。创建成功后扣减商品库存，订单状态为 created。"
        "可传 Idempotency-Key 防止客户端重试产生重复订单。"
    ),
    responses={
        200: {
            "model": OrderResponse,
            "description": "相同 Idempotency-Key 和请求参数的幂等重放",
            "headers": {
                "Idempotency-Replayed": {
                    "description": "true 表示本次响应复用了已有订单",
                    "schema": {"type": "string", "enum": ["true"]},
                }
            },
        },
        201: {
            "model": OrderResponse,
            "description": "订单创建成功",
            "headers": {
                "Idempotency-Replayed": {
                    "description": "false 表示本次请求创建了新订单",
                    "schema": {"type": "string", "enum": ["false"]},
                }
            },
        },
        **AUTH_RESPONSE,
        404: {"model": ErrorResponse, "description": "商品不存在"},
        409: {"model": ErrorResponse, "description": "商品下架、库存不足或幂等键冲突"},
        **VALIDATION_RESPONSE,
    },
)
def create_new_order(
    payload: OrderCreate,
    current_user: CurrentUser,
    db: DbSession,
    response: Response,
    idempotency_key: IdempotencyKey = None,
) -> OrderResponse:
    result = create_order_with_idempotency(db, current_user, payload, idempotency_key)
    response.headers["Idempotency-Replayed"] = str(result.replayed).lower()
    if result.replayed:
        response.status_code = status.HTTP_200_OK
    return result.order


@router.get(
    "",
    response_model=list[OrderResponse],
    summary="查询我的订单列表",
    description="只返回当前登录用户自己的订单，验证用户数据隔离。",
    responses=AUTH_RESPONSE,
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
    responses={
        **AUTH_RESPONSE,
        403: {"model": ErrorResponse, "description": "不能访问其他用户的订单"},
        404: {"model": ErrorResponse, "description": "订单不存在"},
        **VALIDATION_RESPONSE,
    },
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
    responses={
        **AUTH_RESPONSE,
        403: {"model": ErrorResponse, "description": "不能访问其他用户的订单"},
        404: {"model": ErrorResponse, "description": "订单不存在"},
        409: {"model": ErrorResponse, "description": "订单状态不允许支付"},
        **VALIDATION_RESPONSE,
    },
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
    responses={
        **AUTH_RESPONSE,
        403: {"model": ErrorResponse, "description": "不能访问其他用户的订单"},
        404: {"model": ErrorResponse, "description": "订单不存在"},
        409: {"model": ErrorResponse, "description": "订单状态不允许取消"},
        **VALIDATION_RESPONSE,
    },
)
def cancel_existing_order(
    order_id: int,
    current_user: CurrentUser,
    db: DbSession,
) -> OrderResponse:
    return cancel_order(db, current_user, order_id)
