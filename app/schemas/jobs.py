"""Pydantic schemas for the jobs API."""

from pydantic import BaseModel, Field


class JobOut(BaseModel):
    """Canonical job shape shared by API, providers, and persistence."""

    id: str
    source: str
    title: str
    company_name: str
    location: str
    remote: bool
    url: str
    description: str
    tags: list[str]
    job_types: list[str]
    created_at: str | None
    fetched_at: str | None


class SyncResponse(BaseModel):
    """Result of syncing jobs from configured providers."""

    fetched: int
    stored: int
    updated_at: str | None
    by_source: dict[str, int] = Field(default_factory=dict)


class JobsListParams(BaseModel):
    """Query filters for listing jobs."""

    page: int = Field(default=1, ge=1, description="Page number (1-based).")
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Page size (default 20, max 100).",
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
    """Paginated locally stored jobs."""

    updated_at: str | None
    page: int
    limit: int
    total: int
    has_more: bool
    count: int
    jobs: list[JobOut]


class JobResponse(BaseModel):
    """Single job payload."""

    job: JobOut
