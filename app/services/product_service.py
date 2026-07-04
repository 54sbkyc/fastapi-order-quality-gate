from fastapi import status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessException
from app.models.product import Product


def list_products(db: Session) -> list[Product]:
    return list(db.scalars(select(Product).order_by(Product.id)).all())


def get_product(db: Session, product_id: int) -> Product:
    product = db.get(Product, product_id)
    if product is None:
        raise BusinessException(
            "PRODUCT_NOT_FOUND",
            "商品不存在",
            status.HTTP_404_NOT_FOUND,
        )
    return product
