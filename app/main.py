from fastapi import FastAPI

from app.api import routes_auth, routes_orders, routes_products
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.db.base import Base
from app.db.session import engine


def create_app(init_db: bool = True) -> FastAPI:
    app = FastAPI(title=settings.app_name)
    register_exception_handlers(app)

    app.include_router(routes_auth.router)
    app.include_router(routes_products.router)
    app.include_router(routes_orders.router)

    if init_db:
        Base.metadata.create_all(bind=engine)

    return app


app = create_app()
