from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "订单系统接口自动化测试项目"
    app_description: str = (
        "一个用于自动化测试实习简历展示的小型订单系统，"
        "包含 JWT 鉴权、商品查询、订单状态流转、接口自动化测试和 CI 质量门禁。"
    )
    database_url: str = "sqlite:///./order_quality_gate.db"
    jwt_secret_key: str = "change-me-in-real-projects-with-at-least-32-bytes"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
