"""Jobs business logic."""

import logging
from typing import Any, cast

import httpx

from app.config import get_settings
from app.exceptions import UpstreamUnavailableError
from app.providers.arbeitnow import fetch_jobs
from app.schemas.jobs import JobsListParams, JobsListResponse, SyncResponse
from app.store.jobs import load_jobs, upsert_jobs

logger = logging.getLogger(__name__)


def sync_jobs() -> SyncResponse:
    """Fetch jobs from Arbeitnow and upsert them into the local JSON store."""
    settings = get_settings()
    try:
        fetched = fetch_jobs(
            base_url=settings.arbeitnow_base_url,
            max_pages=settings.arbeitnow_max_pages,
        )
    except httpx.HTTPError as exc:
        logger.exception("Arbeitnow sync failed")
        raise UpstreamUnavailableError(
            "Failed to fetch jobs from Arbeitnow",
        ) from exc

    store = upsert_jobs(settings.jobs_data_path, fetched)
    return SyncResponse(
        fetched=len(fetched),
        stored=len(store["jobs"]),
        updated_at=store.get("updated_at"),
    )


def _matches(job: dict[str, Any], params: JobsListParams) -> bool:
    if params.q is not None:
        needle = params.q.casefold()
        title = str(job.get("title") or "").casefold()
        company = str(job.get("company_name") or "").casefold()
        if needle not in title and needle not in company:
            return False

    if params.location is not None:
        job_location = str(job.get("location") or "").casefold()
        if params.location.casefold() not in job_location:
            return False

    if params.remote is not None and bool(job.get("remote")) is not params.remote:
        return False

    if params.tag is not None:
        needle = params.tag.casefold()
        tags = job.get("tags")
        if not isinstance(tags, list):
            return False
        if not any(
            needle in str(item).casefold() for item in cast("list[object]", tags)
        ):
            return False

    return True


def list_jobs(params: JobsListParams) -> JobsListResponse:
    """Return jobs from the local JSON store (no live upstream call)."""
    settings = get_settings()
    store = load_jobs(settings.jobs_data_path)
    stored_jobs = cast("dict[str, dict[str, Any]]", store["jobs"])

    jobs = [job for job in stored_jobs.values() if _matches(job, params)][
        : params.limit
    ]

    updated_at = store.get("updated_at")
    return JobsListResponse(
        updated_at=str(updated_at) if updated_at is not None else None,
        count=len(jobs),
        jobs=jobs,
    )
