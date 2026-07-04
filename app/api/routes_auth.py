from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import TokenResponse, UserCreate, UserLogin, UserResponse
from app.services.auth_service import login_user, register_user

router = APIRouter(prefix="/api/auth", tags=["认证接口"])
DbSession = Annotated[Session, Depends(get_db)]


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="用户注册",
    description="创建一个普通用户账号，用于后续登录和访问订单接口。",
)
def register(payload: UserCreate, db: DbSession) -> UserResponse:
    return register_user(db, payload)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="用户登录",
    description="使用用户名和密码登录，成功后返回 Bearer Token。",
)
def login(payload: UserLogin, db: DbSession) -> TokenResponse:
    access_token = login_user(db, payload)
    return TokenResponse(access_token=access_token)
