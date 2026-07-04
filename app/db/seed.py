from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.product import Product

DEFAULT_PRODUCTS = [
    {"name": "Keyboard", "price": Decimal("199.00"), "stock": 10, "is_active": True},
    {"name": "Mouse", "price": Decimal("99.00"), "stock": 20, "is_active": True},
    {"name": "Monitor", "price": Decimal("899.00"), "stock": 5, "is_active": True},
]


def seed_products(db: Session) -> list[Product]:
    product_names = [product["name"] for product in DEFAULT_PRODUCTS]
    existing_products = db.scalars(
        select(Product).where(Product.name.in_(product_names)).order_by(Product.id)
    ).all()
    existing_by_name = {product.name: product for product in existing_products}

    products = []
    for product_data in DEFAULT_PRODUCTS:
        product = existing_by_name.get(product_data["name"])
        if product is None:
            product = Product(**product_data)
            db.add(product)
        products.append(product)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return list(
            db.scalars(select(Product).where(Product.name.in_(product_names)).order_by(Product.id)).all()
        )

    for product in products:
        db.refresh(product)
    return products
