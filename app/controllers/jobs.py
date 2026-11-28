"""Job sync and list endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.jobs import JobResponse, JobsListParams, JobsListResponse, SyncResponse
from app.service import jobs as jobs_service

router = APIRouter(tags=["jobs"])


@router.post("/jobs/sync", response_model=SyncResponse)
def sync_jobs(session: Annotated[Session, Depends(get_db)]) -> SyncResponse:
    """Fetch jobs from all providers and upsert them into PostgreSQL."""
    return jobs_service.sync_jobs(session)


@router.get("/jobs", response_model=JobsListResponse)
def list_jobs(
    params: Annotated[JobsListParams, Query()],
    session: Annotated[Session, Depends(get_db)],
) -> JobsListResponse:
    """Return a paginated page of jobs from PostgreSQL."""
    return jobs_service.list_jobs(session, params)


@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(
    job_id: str,
    session: Annotated[Session, Depends(get_db)],
) -> JobResponse:
    """Return a single job by id from PostgreSQL."""
    return jobs_service.get_job(session, job_id)
