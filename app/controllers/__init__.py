"""HTTP controllers."""

from fastapi import APIRouter

from app.config import get_settings
from app.controllers.health import router as health_router
from app.controllers.jobs import router as jobs_router

settings = get_settings()

api_router = APIRouter(prefix=settings.api_v1_prefix)
api_router.include_router(health_router)
api_router.include_router(jobs_router)
