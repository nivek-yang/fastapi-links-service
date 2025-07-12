import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel


# 定義一個通用的響應模型
class APIResponse(BaseModel):
    success: bool
    message: str


# 定義 MongoDB 連接資訊
MONGO_HOST = os.environ.get("MONGO_HOST", "localhost")
MONGO_PORT = int(os.environ.get("MONGO_PORT", 27017))
MONGO_DB = os.environ.get("MONGO_DB", "links_db")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.mongodb_client = AsyncIOMotorClient(f"mongodb://{MONGO_HOST}:{MONGO_PORT}")
    app.mongodb = app.mongodb_client[MONGO_DB]
    print(f"Connected to MongoDB: {MONGO_DB} on {MONGO_HOST}:{MONGO_PORT}")
    # 強制檢查連線
    try:
        await app.mongodb.list_collection_names()
        print("MongoDB connection test passed.")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        # 可以選擇 raise 或只警告
    yield
    app.mongodb_client.close()
    print("Disconnected from MongoDB.")


app = FastAPI(
    title="FastAPI Links Service",
    description="API service for managing short links.",
    version="0.1.0",
    lifespan=lifespan,  # 將 lifespan 傳遞給 FastAPI 應用
)


@app.get("/health", tags=["Health Check"], response_model=APIResponse)
async def health_check():
    """
    Health check endpoint to verify service status.
    """
    return APIResponse(success=True, message="FastAPI Links Service is running!")


# 測試 MongoDB 連接的端點
@app.get("/db-check", tags=["Health Check"], response_model=APIResponse)
async def db_check():
    """
    Check MongoDB connection status.
    """
    try:
        # 嘗試列出一個集合，以驗證連接是否活躍
        await app.mongodb.list_collection_names()
        return APIResponse(success=True, message="MongoDB connection is successful!")
    except Exception as e:
        return APIResponse(success=False, message=f"MongoDB connection failed: {e}")


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
