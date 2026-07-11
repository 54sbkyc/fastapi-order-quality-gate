from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(prefix="/api", tags=["系统接口"])


@router.get(
    "/health",
    summary="健康检查",
    description="返回服务状态和版本信息，用于本地演示、前端连通性检查和 CI 冒烟验证。",
)
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": "0.1.0",
    }
