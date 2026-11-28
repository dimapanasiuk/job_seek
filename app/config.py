"""Application settings loaded from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app import __version__


class Settings(BaseSettings):
    """Runtime configuration for the Jobseek service."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "jobseek"
    app_version: str = __version__
    environment: Literal["local", "dev", "staging", "prod"] = "local"
    debug: bool = False
    log_level: str = "INFO"
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = Field(default_factory=list)
    arbeitnow_base_url: str = "https://www.arbeitnow.com/api/job-board-api"
    arbeitnow_max_pages: int = 5
    jobicy_base_url: str = "https://jobicy.com/api/jobs"
    jobicy_max_pages: int = 5
    jobicy_count: int = 200
    database_url: str = "postgresql+psycopg://jobseek:jobseek@localhost:5432/jobseek"


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
