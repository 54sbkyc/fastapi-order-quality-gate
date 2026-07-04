from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.get("")
def list_orders(current_user: User = Depends(get_current_user)) -> list[dict[str, int]]:
    return []

