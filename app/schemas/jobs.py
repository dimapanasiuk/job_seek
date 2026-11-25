"""Pydantic schemas for the jobs API."""

from typing import Any

from pydantic import BaseModel, Field


class SyncResponse(BaseModel):
    """Result of syncing jobs from Arbeitnow."""

    fetched: int
    stored: int
    updated_at: str | None


class JobsListParams(BaseModel):
    """Query filters for listing jobs."""

    limit: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Max jobs to return (default 100).",
    )
    q: str | None = Field(
        default=None,
        min_length=1,
        description="Search in title and company name (case-insensitive).",
    )
    location: str | None = Field(
        default=None,
        min_length=1,
        description="Filter by location substring (case-insensitive).",
    )
    remote: bool | None = Field(
        default=None,
        description="If set, only remote or only on-site jobs.",
    )
    tag: str | None = Field(
        default=None,
        min_length=1,
        description="Filter by tag substring (case-insensitive).",
    )


class JobsListResponse(BaseModel):
    """Locally stored jobs."""

    updated_at: str | None
    count: int
    jobs: list[dict[str, Any]]
