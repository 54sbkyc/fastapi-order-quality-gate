from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class OrderCreate(BaseModel):
    product_id: int = Field(description="商品 ID")
    quantity: int = Field(gt=0, le=100, description="购买数量，必须在 1 到 100 之间")


class OrderResponse(BaseModel):
    id: int = Field(description="订单 ID")
    user_id: int = Field(description="用户 ID")
    product_id: int = Field(description="商品 ID")
    quantity: int = Field(description="购买数量")
    total_amount: Decimal = Field(description="订单总金额")
    status: str = Field(description="订单状态：created、paid、cancelled")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")

    model_config = ConfigDict(from_attributes=True)
