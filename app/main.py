from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api import routes_auth, routes_health, routes_orders, routes_products
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.db.base import Base
from app.db.seed import seed_products
from app.db.session import SessionLocal, engine

FRONTEND_DIST = Path(__file__).resolve().parents[1] / "frontend" / "dist"


def create_app(init_db: bool = True) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI):
        if init_db:
            Base.metadata.create_all(bind=engine)
            with SessionLocal() as db:
                seed_products(db)
        yield

    app = FastAPI(
        title=settings.app_name,
        description=settings.app_description,
        version="0.1.0",
        lifespan=lifespan,
        openapi_tags=[
            {"name": "认证接口", "description": "用户注册、登录和 JWT 鉴权。"},
            {"name": "商品接口", "description": "商品列表和商品详情查询。"},
            {"name": "订单接口", "description": "订单创建、查询、支付模拟和取消。"},
            {"name": "系统接口", "description": "服务健康检查和演示连通性验证。"},
        ],
    )
    register_exception_handlers(app)

    app.include_router(routes_health.router)
    app.include_router(routes_auth.router)
    app.include_router(routes_products.router)
    app.include_router(routes_orders.router)

    if FRONTEND_DIST.is_dir():
        app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")

    return app


app = create_app()
