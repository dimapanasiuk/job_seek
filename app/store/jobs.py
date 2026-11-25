"""JSON-file persistence for synced jobs."""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast


def _empty_store() -> dict[str, Any]:
    return {"updated_at": None, "jobs": {}}


def load_jobs(path: str | Path) -> dict[str, Any]:
    """Load the jobs store from disk, or return an empty store if missing."""
    file_path = Path(path)
    if not file_path.exists():
        return _empty_store()

    with file_path.open(encoding="utf-8") as handle:
        data = cast("object", json.load(handle))

    if not isinstance(data, dict):
        return _empty_store()

    typed_data = cast("dict[str, Any]", data)
    raw_jobs = typed_data.get("jobs")
    jobs: dict[str, dict[str, Any]] = {}
    if isinstance(raw_jobs, dict):
        for key, value in cast("dict[Any, Any]", raw_jobs).items():
            if isinstance(value, dict):
                jobs[str(key)] = cast("dict[str, Any]", value)

    updated_at = typed_data.get("updated_at")
    return {
        "updated_at": str(updated_at) if updated_at is not None else None,
        "jobs": jobs,
    }


def save_jobs(path: str | Path, jobs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Replace the jobs map on disk and return the written store payload."""
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    payload: dict[str, Any] = {
        "updated_at": datetime.now(tz=UTC).isoformat(),
        "jobs": jobs,
    }
    with file_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    return payload


def upsert_jobs(
    path: str | Path,
    incoming: list[dict[str, Any]],
) -> dict[str, Any]:
    """Merge incoming jobs into the store by id and persist."""
    store = load_jobs(path)
    jobs = cast("dict[str, dict[str, Any]]", store["jobs"])
    for job in incoming:
        job_id = job.get("id")
        if not job_id:
            continue
        jobs[str(job_id)] = job
    return save_jobs(path, jobs)
