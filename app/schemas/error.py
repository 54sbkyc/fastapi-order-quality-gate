from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    code: str = Field(description="业务错误码")
    message: str = Field(description="错误说明")
