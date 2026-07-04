from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50, description="用户名")
    password: str = Field(min_length=6, max_length=128, description="密码")


class UserLogin(BaseModel):
    username: str = Field(description="用户名")
    password: str = Field(description="密码")


class UserResponse(BaseModel):
    id: int = Field(description="用户 ID")
    username: str = Field(description="用户名")

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str = Field(description="JWT 访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
