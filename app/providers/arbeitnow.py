"""Arbeitnow job board API client."""

from datetime import UTC, datetime
from typing import Any, cast

import httpx

SOURCE = "arbeitnow"


def _as_str_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in cast("list[object]", value)]


def _created_at_iso(value: object) -> str | None:
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=UTC).isoformat()
    if value is None:
        return None
    return str(value)


def _job_id(raw: dict[str, Any]) -> str:
    slug = str(raw.get("slug") or "")
    return f"{SOURCE}:{slug or raw.get('url')}"


def _normalize_job(raw: dict[str, Any], *, fetched_at: str) -> dict[str, Any]:
    """Map an Arbeitnow payload item to our local job shape."""
    return {
        "id": _job_id(raw),
        "source": SOURCE,
        "title": raw.get("title"),
        "company_name": raw.get("company_name"),
        "location": raw.get("location"),
        "remote": bool(raw.get("remote")),
        "url": raw.get("url"),
        "description": raw.get("description"),
        "tags": _as_str_list(raw.get("tags")),
        "job_types": _as_str_list(raw.get("job_types")),
        "created_at": _created_at_iso(raw.get("created_at")),
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


def _has_next_page(payload: dict[str, Any]) -> bool:
    links = payload.get("links")
    if not isinstance(links, dict):
        return False
    return bool(cast("dict[str, object]", links).get("next"))


def _fetch_page(
    client: httpx.Client,
    *,
    base_url: str,
    page: int,
) -> dict[str, Any] | None:
    response = client.get(base_url, params={"page": page})
    response.raise_for_status()
    payload = cast("object", response.json())
    return cast("dict[str, Any]", payload) if isinstance(payload, dict) else None


def fetch_jobs(
    *,
    base_url: str,
    max_pages: int,
    timeout: float = 30.0,
) -> list[dict[str, Any]]:
    """Fetch and normalize jobs from Arbeitnow across ``1..max_pages``."""
    if max_pages < 1:
        return []

    fetched_at = datetime.now(tz=UTC).isoformat()
    jobs: list[dict[str, Any]] = []

    with httpx.Client(timeout=timeout) as client:
        for page in range(1, max_pages + 1):
            payload = _fetch_page(client, base_url=base_url, page=page)
            if payload is None:
                break

            page_jobs = _dict_list(payload.get("data"))
            if not page_jobs:
                break

            jobs.extend(
                _normalize_job(item, fetched_at=fetched_at) for item in page_jobs
            )
            if not _has_next_page(payload):
                break

    return jobs
