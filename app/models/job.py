"""Job ORM model."""

from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Job(Base):
    """Persisted job vacancy from an external provider."""

    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    source: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    company_name: Mapped[str] = mapped_column(Text, nullable=False, default="")
    location: Mapped[str] = mapped_column(Text, nullable=False, default="")
    remote: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    url: Mapped[str] = mapped_column(Text, nullable=False, default="")
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    tags: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    job_types: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    fetched_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def to_dict(self) -> dict[str, Any]:
        """Serialize the row to the API/provider job shape."""
        return {
            "id": self.id,
            "source": self.source,
            "title": self.title,
            "company_name": self.company_name,
            "location": self.location,
            "remote": self.remote,
            "url": self.url,
            "description": self.description,
            "tags": list(self.tags),
            "job_types": list(self.job_types),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "fetched_at": self.fetched_at.isoformat() if self.fetched_at else None,
        }
