import pytest
from httpx import AsyncClient
from main import app  # 導入 FastAPI 應用實例

# 使用 pytest-asyncio 確保測試函式可以是非同步的
# @pytest.mark.asyncio 裝飾器會自動處理事件循環


@pytest.fixture(scope="module")
async def async_client():
    """
    Fixture to create an asynchronous test client for FastAPI app.
    This client will be used across all tests in this module.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient):
    """
    Test the /health endpoint.
    """
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "message": "FastAPI Links Service is running!",
    }


@pytest.mark.asyncio
async def test_db_check(async_client: AsyncClient):
    """
        Test the /db-check endpoint.
        This test assumes MongoDB is running and accessible at the configured
    host/port.
    """
    response = await async_client.get("/db-check")
    assert response.status_code == 200
    # 由於 MongoDB 可能需要一些時間啟動，這裡只檢查 success 字段
    # 實際的錯誤訊息可能因環境而異
    assert response.json()["success"] is True
    assert "MongoDB connection is successful!" in response.json()["message"]
