from typing import Optional
from pydantic import BaseModel, Field, HttpUrl


# 定義一個通用的響應模型
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None


class CreateLinkRequest(BaseModel):
    original_url: HttpUrl = Field(..., description="The original URL to shorten.")
    slug: Optional[str] = Field(None, min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$", description="Optional custom short URL slug.")
    password: Optional[str] = Field(None, min_length=4, max_length=64, description="Optional password for the short link.")
    is_active: bool = Field(True, description="Whether the link is active.")
    notes: Optional[str] = Field(None, description="Optional notes for the link.")

    class Config:
        json_schema_extra = {
            "example": {
                "original_url": "https://www.example.com/very/long/url",
                "slug": "mycustomlink",
                "password": "securepass",
                "is_active": True,
                "notes": "This is a test link."
            }
        }