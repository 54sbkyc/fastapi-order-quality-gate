from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.schemas.order import OrderCreate, OrderResponse
from app.models.user import User
from app.services.order_service import (
    cancel_order,
    create_order,
    get_user_order,
    list_user_orders,
    pay_order,
)

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_new_order(
    payload: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrderResponse:
    return create_order(db, current_user, payload)


@router.get("", response_model=list[OrderResponse])
def list_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[OrderResponse]:
    return list_user_orders(db, current_user)


@router.get("/{order_id}", response_model=OrderResponse)
def get_order_detail(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrderResponse:
    return get_user_order(db, current_user, order_id)


@router.post("/{order_id}/pay", response_model=OrderResponse)
def pay_existing_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrderResponse:
    return pay_order(db, current_user, order_id)


@router.post("/{order_id}/cancel", response_model=OrderResponse)
def cancel_existing_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrderResponse:
    return cancel_order(db, current_user, order_id)
