from fastapi import FastAPI, status
from pydantic import BaseModel


# 定義一個通用的響應模型，只包含 success 和 message
class APIResponse(BaseModel):
    success: bool
    message: str


app = FastAPI(
    title="FastAPI Links Service",
    description="API service for managing short links.",
    version="0.1.0",
)


@app.get("/health", tags=["Health Check"], response_model=APIResponse)
async def health_check():
    """
    Health check endpoint to verify service status.
    """
    return APIResponse(success=True, message="FastAPI Links Service is running!")


# 範例：一個模擬的短網址創建端點，展示如何使用 APIResponse 和自定義狀態碼
@app.post(
    "/links",
    tags=["Links"],
    status_code=status.HTTP_201_CREATED,
    response_model=APIResponse,
)
async def create_link_example():
    """
    Example endpoint to demonstrate Django-like JSON response.
    """
    # 這裡會是實際創建短網址的邏輯
    # 注意：short_url 和 original_url 不再是 APIResponse 的一部分

    return APIResponse(
        success=True,
        message="Link created successfully.",
    )


# 範例：一個模擬的錯誤響應
@app.post(
    "/links/error",
    tags=["Links"],
    status_code=status.HTTP_400_BAD_REQUEST,
    response_model=APIResponse,
)
async def create_link_error_example():
    """
    Example endpoint to demonstrate an error response.
    """
    return APIResponse(
        success=False,
        message="Original URL is required.",
    )
