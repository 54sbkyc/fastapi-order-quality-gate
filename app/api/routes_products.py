from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.product import ProductResponse
from app.services.product_service import get_product, list_products

router = APIRouter(prefix="/api/products", tags=["商品接口"])
DbSession = Annotated[Session, Depends(get_db)]


@router.get(
    "",
    response_model=list[ProductResponse],
    summary="查询商品列表",
    description="返回系统中已初始化的商品数据，用于创建订单测试。",
)
def get_products(db: DbSession) -> list[ProductResponse]:
    return list_products(db)


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="查询商品详情",
    description="根据商品 ID 查询商品详情，商品不存在时返回业务错误码。",
)
def get_product_detail(product_id: int, db: DbSession) -> ProductResponse:
    return get_product(db, product_id)
