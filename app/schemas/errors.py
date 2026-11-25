"""Pydantic schemas for API error responses."""

from typing import Any

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Stable error envelope for clients."""

    error: str
    message: str
    details: Any | None = None
