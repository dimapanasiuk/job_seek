"""Job sync and list endpoints."""

from typing import Annotated

from fastapi import APIRouter, Query

from app.schemas.jobs import JobsListParams, JobsListResponse, SyncResponse
from app.service import jobs as jobs_service

router = APIRouter(tags=["jobs"])


@router.post("/jobs/sync", response_model=SyncResponse)
def sync_jobs() -> SyncResponse:
    """Fetch jobs from Arbeitnow and upsert them into the local JSON store."""
    return jobs_service.sync_jobs()


@router.get("/jobs", response_model=JobsListResponse)
def list_jobs(
    params: Annotated[JobsListParams, Query()],
) -> JobsListResponse:
    """Return jobs from the local JSON store (no live upstream call)."""
    return jobs_service.list_jobs(params)
