from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ProductResponse(BaseModel):
    id: int
    name: str
    price: Decimal
    stock: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

