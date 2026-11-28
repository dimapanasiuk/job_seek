"""PostgreSQL persistence for synced jobs."""

from datetime import UTC, datetime
from typing import Any, cast

from sqlalchemy import ColumnElement, func, or_, select
from sqlalchemy import cast as sa_cast
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select
from sqlalchemy.types import Text

from app.models.job import Job
from app.schemas.jobs import JobOut, JobsListParams


def _ensure_aware(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value


def _parse_datetime(value: object) -> datetime | None:
    if isinstance(value, datetime):
        return _ensure_aware(value)
    if not isinstance(value, str) or not value.strip():
        return None
    normalized = value.strip().replace("Z", "+00:00")
    try:
        return _ensure_aware(datetime.fromisoformat(normalized))
    except ValueError:
        return None


def _as_str(value: object, default: str = "") -> str:
    if value is None:
        return default
    return str(value)


def _as_str_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    items = cast("list[object]", value)
    return [str(item) for item in items]


def _job_row_values(job: dict[str, Any], *, now: datetime) -> dict[str, Any] | None:
    job_id = job.get("id")
    if not job_id:
        return None
    return {
        "id": str(job_id),
        "source": _as_str(job.get("source")),
        "title": _as_str(job.get("title")),
        "company_name": _as_str(job.get("company_name")),
        "location": _as_str(job.get("location")),
        "remote": bool(job.get("remote")),
        "url": _as_str(job.get("url")),
        "description": _as_str(job.get("description")),
        "tags": _as_str_list(job.get("tags")),
        "job_types": _as_str_list(job.get("job_types")),
        "created_at": _parse_datetime(job.get("created_at")),
        "fetched_at": _parse_datetime(job.get("fetched_at")),
        "updated_at": now,
    }


def _to_job_out(row: Job) -> JobOut:
    return JobOut.model_validate(row.to_dict())


def count_jobs(session: Session) -> int:
    """Return the total number of stored jobs."""
    return int(session.scalar(select(func.count()).select_from(Job)) or 0)


def max_updated_at(session: Session) -> str | None:
    """Return the latest job `updated_at` as an ISO timestamp, if any."""
    value = session.scalar(select(func.max(Job.updated_at)))
    if value is None:
        return None
    return value.isoformat()


def upsert_jobs(session: Session, incoming: list[dict[str, Any]]) -> dict[str, Any]:
    """Merge incoming jobs by id and return sync metadata."""
    now = datetime.now(tz=UTC)
    rows = [
        values
        for job in incoming
        if (values := _job_row_values(job, now=now)) is not None
    ]
    if rows:
        stmt = insert(Job).values(rows)
        update_cols: dict[str, ColumnElement[Any]] = {
            "source": stmt.excluded.source,
            "title": stmt.excluded.title,
            "company_name": stmt.excluded.company_name,
            "location": stmt.excluded.location,
            "remote": stmt.excluded.remote,
            "url": stmt.excluded.url,
            "description": stmt.excluded.description,
            "tags": stmt.excluded.tags,
            "job_types": stmt.excluded.job_types,
            "created_at": stmt.excluded.created_at,
            "fetched_at": stmt.excluded.fetched_at,
            "updated_at": stmt.excluded.updated_at,
        }
        session.execute(
            stmt.on_conflict_do_update(index_elements=["id"], set_=update_cols)
        )
        session.commit()

    return {
        "updated_at": max_updated_at(session) or now.isoformat(),
        "stored": count_jobs(session),
    }


def _filter_clauses(params: JobsListParams) -> list[ColumnElement[bool]]:
    clauses: list[ColumnElement[bool]] = []

    if params.q is not None:
        pattern = f"%{params.q}%"
        clauses.append(or_(Job.title.ilike(pattern), Job.company_name.ilike(pattern)))

    if params.location is not None:
        clauses.append(Job.location.ilike(f"%{params.location}%"))

    if params.remote is not None:
        clauses.append(Job.remote.is_(params.remote))

    if params.tag is not None:
        tag_pattern = f"%{params.tag}%"
        tag_element = func.jsonb_array_elements_text(Job.tags).table_valued("value")
        clauses.append(
            select(1)
            .select_from(tag_element)
            .where(sa_cast(tag_element.c.value, Text).ilike(tag_pattern))
            .correlate(Job)
            .exists()
        )

    return clauses


def _filtered_select(params: JobsListParams) -> Select[Any]:
    stmt: Select[Any] = select(Job)
    for clause in _filter_clauses(params):
        stmt = stmt.where(clause)
    return stmt


def list_jobs(
    session: Session,
    params: JobsListParams,
) -> dict[str, Any]:
    """Return a filtered, paginated page of jobs plus list metadata."""
    filtered = _filtered_select(params)
    total = int(
        session.scalar(select(func.count()).select_from(filtered.subquery())) or 0
    )
    offset = (params.page - 1) * params.limit
    page_rows = session.scalars(
        filtered.order_by(Job.updated_at.desc(), Job.id)
        .offset(offset)
        .limit(params.limit)
    ).all()

    return {
        "updated_at": max_updated_at(session),
        "total": total,
        "jobs": [_to_job_out(row) for row in page_rows],
    }


def get_job(session: Session, job_id: str) -> JobOut | None:
    """Return one job by id, or None if missing."""
    row = session.get(Job, job_id)
    if row is None:
        return None
    return _to_job_out(row)
