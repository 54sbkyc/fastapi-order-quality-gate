from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.product import ProductResponse
from app.services.product_service import get_product, list_products

router = APIRouter(prefix="/api/products", tags=["products"])
DbSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[ProductResponse])
def get_products(db: DbSession) -> list[ProductResponse]:
    return list_products(db)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product_detail(product_id: int, db: DbSession) -> ProductResponse:
    return get_product(db, product_id)
