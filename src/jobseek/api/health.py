"""Health check endpoint."""

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from jobseek import __version__

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Health check payload."""

    status: Literal["ok"]
    version: str


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Return service liveness and version."""
    return HealthResponse(status="ok", version=__version__)
