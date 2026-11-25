"""Root API v1 router."""

from fastapi import APIRouter

from jobseek.api import health
from jobseek.config import get_settings

settings = get_settings()

api_router = APIRouter(prefix=settings.api_v1_prefix)
api_router.include_router(health.router)
