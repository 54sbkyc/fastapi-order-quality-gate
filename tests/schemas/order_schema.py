from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class OrderResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    total_amount: Decimal
    status: str
    created_at: datetime
    updated_at: datetime

