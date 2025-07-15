import hashlib
import os
from contextlib import asynccontextmanager
from datetime import datetime

import constants
import security
import utils
from beanie import init_beanie
from exception_handlers import http_exception_handler, validation_exception_handler
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.exceptions import RequestValidationError
from models import Link
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from pydantic import HttpUrl
from pydantic import ValidationError as PydanticValidationError
from schemas import APIResponse, CreateLinkRequest
from starlette.exceptions import HTTPException as StarletteHTTPException

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
        await init_beanie(database=app.mongodb, document_models=[Link])
        print("Beanie ODM initialized.")
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

# Register custom exception handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)


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


@app.post(
    "/links",
    tags=["Links"],
    status_code=status.HTTP_201_CREATED,
    response_model=APIResponse,
)
async def create_link(
    request: CreateLinkRequest,
    current_user: security.TokenData = Depends(security.get_current_user),
):
    """
    Create a new short link.
    - If a custom slug is provided, it will be used.
    - Otherwise, a random slug will be generated.
    """
    # Validate original_url format using Pydantic's HttpUrl
    try:
        HttpUrl(str(request.original_url))
    except PydanticValidationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=constants.URL_INVALID_ERROR,
        )

    # Handle custom slug or generate a new one
    if request.slug:
        # Check if custom slug already exists using Beanie
        if await Link.find_one(Link.slug == request.slug):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=constants.SLUG_DUPLICATE_ERROR,
            )
        slug = request.slug
    else:
        # Generate a unique random slug
        slug = utils.generate_slug()
        while await Link.find_one(Link.slug == slug):
            slug = utils.generate_slug()

    # Hash password if provided
    hashed_password = None
    if request.password:
        hashed_password = pwd_context.hash(request.password)

    # Generate original_url_hash
    original_url_hash = hashlib.sha256(str(request.original_url).encode()).hexdigest()

    # Check for existing link with the same original_url_hash (reverse lookup)
    # This is for optimization, not strict uniqueness enforcement for original_url
    existing_link = await Link.find_one(Link.original_url_hash == original_url_hash)
    if existing_link:
        # If an existing link is found, return its slug for efficiency
        return APIResponse(
            success=True,
            message=constants.CREATED_LINK_SUCCESS,
            data={
                "slug": existing_link.slug,
                "original_url": existing_link.original_url,
            },
        )

    # Create a Link document instance
    new_link = Link(
        original_url=str(request.original_url),
        original_url_hash=original_url_hash,
        slug=slug,
        owner_id=current_user.user_id,  # From JWT
        password=hashed_password,
        is_active=request.is_active,
        created_at=datetime.utcnow(),
        expires_at=None,  # Not implemented yet
        click_count=0,
        notes=request.notes,
    )

    await new_link.insert()

    return APIResponse(
        success=True,
        message=constants.CREATED_LINK_SUCCESS,
        data={"slug": slug, "original_url": str(request.original_url)},
    )


@app.get("/users/me", tags=["Users"], response_model=security.TokenData)
async def read_users_me(
    current_user: security.TokenData = Depends(security.get_current_user),
):
    return current_user
