"""CP1 - 12-Factor configuration.

Principle: no config value lives in code. Everything comes from environment
variables so the same image runs on laptop, staging, and production.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Full service configuration, sourced from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    port: int = 8000
    agent_api_key: str
    redis_url: str = "redis://localhost:6379/0"
    rate_limit_per_minute: int = 10
    monthly_budget_usd: float = 10.0
    log_level: str = "INFO"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Read configuration once and cache it."""
    return Settings()
