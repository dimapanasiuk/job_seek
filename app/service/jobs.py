"""Jobs business logic."""

import logging
from typing import Any

import httpx
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.exceptions import NotFoundError, UpstreamUnavailableError
from app.providers import arbeitnow, jobicy
from app.repositories import jobs as jobs_repo
from app.schemas.jobs import JobResponse, JobsListParams, JobsListResponse, SyncResponse

logger = logging.getLogger(__name__)


def _collect_from_providers(
    settings: Settings,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    fetched: list[dict[str, Any]] = []
    by_source: dict[str, int] = {}
    errors: list[str] = []

    try:
        arbeitnow_jobs = arbeitnow.fetch_jobs(
            base_url=settings.arbeitnow_base_url,
            max_pages=settings.arbeitnow_max_pages,
        )
    except httpx.HTTPError:
        logger.exception("arbeitnow sync failed")
        errors.append("arbeitnow")
        by_source["arbeitnow"] = 0
    else:
        by_source["arbeitnow"] = len(arbeitnow_jobs)
        fetched.extend(arbeitnow_jobs)

    try:
        jobicy_jobs = jobicy.fetch_jobs(
            base_url=settings.jobicy_base_url,
            max_pages=settings.jobicy_max_pages,
            count=settings.jobicy_count,
        )
    except httpx.HTTPError:
        logger.exception("jobicy sync failed")
        errors.append("jobicy")
        by_source["jobicy"] = 0
    else:
        by_source["jobicy"] = len(jobicy_jobs)
        fetched.extend(jobicy_jobs)

    if errors and not fetched:
        raise UpstreamUnavailableError(
            "Failed to fetch jobs from all providers",
            details={"failed": errors},
        )

    if errors:
        logger.warning("Partial sync; failed providers: %s", ", ".join(errors))

    return fetched, by_source


def sync_jobs(session: Session) -> SyncResponse:
    """Fetch jobs from all providers and upsert them into PostgreSQL."""
    settings = get_settings()
    fetched, by_source = _collect_from_providers(settings)
    result = jobs_repo.upsert_jobs(session, fetched)
    return SyncResponse(
        fetched=len(fetched),
        stored=int(result["stored"]),
        updated_at=result.get("updated_at"),
        by_source=by_source,
    )


def list_jobs(session: Session, params: JobsListParams) -> JobsListResponse:
    """Return a page of jobs from PostgreSQL."""
    result = jobs_repo.list_jobs(session, params)
    jobs = result["jobs"]
    total = int(result["total"])
    offset = (params.page - 1) * params.limit
    return JobsListResponse(
        updated_at=result.get("updated_at"),
        page=params.page,
        limit=params.limit,
        total=total,
        has_more=offset + len(jobs) < total,
        count=len(jobs),
        jobs=jobs,
    )


def get_job(session: Session, job_id: str) -> JobResponse:
    """Return one job by id from PostgreSQL."""
    job = jobs_repo.get_job(session, job_id)
    if job is None:
        raise NotFoundError(
            f"Job not found: {job_id}",
            details={"job_id": job_id},
        )
    return JobResponse(job=job)
