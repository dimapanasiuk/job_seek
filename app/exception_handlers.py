"""FastAPI exception handlers with a shared error envelope."""

import logging
from typing import Any, cast

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.exceptions import AppError
from app.schemas.errors import ErrorResponse

logger = logging.getLogger(__name__)


def _error_response(
    *,
    status_code: int,
    error: str,
    message: str,
    details: Any | None = None,
) -> JSONResponse:
    payload = ErrorResponse(error=error, message=message, details=details)
    return JSONResponse(status_code=status_code, content=payload.model_dump())


async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    """Map domain AppError to the shared JSON envelope."""
    logger.warning("AppError %s: %s", exc.code, exc.message)
    return _error_response(
        status_code=exc.status_code,
        error=exc.code,
        message=exc.message,
        details=exc.details,
    )


async def validation_error_handler(
    _request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Normalize request validation failures to the shared envelope."""
    details = cast("list[Any]", exc.errors())
    return _error_response(
        status_code=422,
        error="validation_error",
        message="Request validation failed",
        details=details,
    )


async def unhandled_error_handler(_request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for unexpected errors; never leak traceback to clients."""
    logger.error("Unhandled error: %s", exc, exc_info=exc)
    return _error_response(
        status_code=500,
        error="internal_error",
        message="Internal server error",
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Attach application exception handlers to the FastAPI app."""
    app.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_error_handler)
