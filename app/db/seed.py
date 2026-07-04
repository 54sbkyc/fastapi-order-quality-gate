from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product


DEFAULT_PRODUCTS = [
    {"name": "Keyboard", "price": Decimal("199.00"), "stock": 10, "is_active": True},
    {"name": "Mouse", "price": Decimal("99.00"), "stock": 20, "is_active": True},
    {"name": "Monitor", "price": Decimal("899.00"), "stock": 5, "is_active": True},
]


def seed_products(db: Session) -> list[Product]:
    existing_products = db.scalars(select(Product).order_by(Product.id)).all()
    if existing_products:
        return list(existing_products)

    products = [Product(**product_data) for product_data in DEFAULT_PRODUCTS]
    db.add_all(products)
    db.commit()
    for product in products:
        db.refresh(product)
    return products

