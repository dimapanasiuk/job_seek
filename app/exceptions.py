"""Application-level exceptions mapped to HTTP responses."""

from typing import Any


class AppError(Exception):
    """Base error with HTTP status and stable client-facing code."""

    def __init__(
        self,
        message: str,
        *,
        code: str,
        status_code: int,
        details: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details


class UpstreamUnavailableError(AppError):
    """External provider could not be reached or returned an error."""

    def __init__(
        self,
        message: str = "Failed to fetch jobs from upstream provider",
        *,
        details: Any | None = None,
    ) -> None:
        super().__init__(
            message,
            code="upstream_unavailable",
            status_code=502,
            details=details,
        )


class NotFoundError(AppError):
    """Requested resource does not exist."""

    def __init__(
        self,
        message: str = "Resource not found",
        *,
        details: Any | None = None,
    ) -> None:
        super().__init__(
            message,
            code="not_found",
            status_code=404,
            details=details,
        )
