"""Jobicy remote jobs API client."""

from datetime import UTC, datetime
from typing import Any, cast

import httpx

SOURCE = "jobicy"


def _as_str_list(value: object) -> list[str]:
    if isinstance(value, str):
        return [value] if value else []
    if not isinstance(value, list):
        return []
    return [str(item) for item in cast("list[object]", value) if item is not None]


def _job_id(raw: dict[str, Any]) -> str:
    raw_id = raw.get("id")
    if raw_id is not None:
        return f"{SOURCE}:{raw_id}"
    slug = str(raw.get("jobSlug") or raw.get("url") or "")
    return f"{SOURCE}:{slug}"


def _normalize_job(raw: dict[str, Any], *, fetched_at: str) -> dict[str, Any]:
    """Map a Jobicy payload item to our local job shape."""
    industries = _as_str_list(raw.get("jobIndustry"))
    level = raw.get("jobLevel")
    tags = industries.copy()
    if level:
        tags.append(str(level))

    created_at = raw.get("pubDate")
    return {
        "id": _job_id(raw),
        "source": SOURCE,
        "title": raw.get("jobTitle"),
        "company_name": raw.get("companyName"),
        "location": raw.get("jobGeo"),
        "remote": True,
        "url": raw.get("url"),
        "description": raw.get("jobDescription") or raw.get("jobExcerpt"),
        "tags": tags,
        "job_types": _as_str_list(raw.get("jobType")),
        "created_at": str(created_at) if created_at is not None else None,
        "fetched_at": fetched_at,
    }


def _dict_list(value: object) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [
        cast("dict[str, Any]", item)
        for item in cast("list[object]", value)
        if isinstance(item, dict)
    ]


def _fetch_page(
    client: httpx.Client,
    *,
    base_url: str,
    count: int,
    cursor: str | None,
) -> dict[str, Any] | None:
    params: dict[str, str | int] = {"count": count}
    if cursor:
        params["cursor"] = cursor
    response = client.get(base_url, params=params)
    response.raise_for_status()
    payload = cast("object", response.json())
    return cast("dict[str, Any]", payload) if isinstance(payload, dict) else None


def fetch_jobs(
    *,
    base_url: str,
    max_pages: int,
    count: int = 200,
    timeout: float = 30.0,
) -> list[dict[str, Any]]:
    """Fetch and normalize jobs from Jobicy across up to ``max_pages``."""
    if max_pages < 1:
        return []

    fetched_at = datetime.now(tz=UTC).isoformat()
    jobs: list[dict[str, Any]] = []
    cursor: str | None = None

    with httpx.Client(timeout=timeout) as client:
        for _ in range(max_pages):
            payload = _fetch_page(
                client,
                base_url=base_url,
                count=count,
                cursor=cursor,
            )
            if payload is None:
                break

            page_jobs = _dict_list(payload.get("jobs"))
            if not page_jobs:
                break

            jobs.extend(
                _normalize_job(item, fetched_at=fetched_at) for item in page_jobs
            )

            next_cursor = payload.get("nextCursor")
            has_more = bool(payload.get("hasMore"))
            if not has_more or not isinstance(next_cursor, str) or not next_cursor:
                break
            cursor = next_cursor

    return jobs
