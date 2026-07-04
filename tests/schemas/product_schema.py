from decimal import Decimal

from pydantic import BaseModel


class ProductResponse(BaseModel):
    id: int
    name: str
    price: Decimal
    stock: int
    is_active: bool

