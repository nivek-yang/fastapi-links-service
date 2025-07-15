from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from schemas import APIResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Global handler for Starlette/FastAPI's own HTTPException.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse(success=False, message=exc.detail).model_dump(),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Global handler for Pydantic's RequestValidationError.
    Extracts a user-friendly error message.
    """
    # For Pydantic validation errors, extract the first error message
    error_message = exc.errors()[0]["msg"] if exc.errors() else "Validation error."
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=APIResponse(success=False, message=error_message).model_dump(),
    )
