from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductResponse(BaseModel):
    id: int = Field(description="商品 ID")
    name: str = Field(description="商品名称")
    price: Decimal = Field(description="商品单价")
    stock: int = Field(description="库存数量")
    is_active: bool = Field(description="是否上架")

    model_config = ConfigDict(from_attributes=True)
