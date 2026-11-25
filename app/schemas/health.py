"""Pydantic schemas for the health API."""

from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check payload."""

    status: Literal["ok"]
    version: str
