"""Application configuration."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables and .env."""

    app_name: str = "JobFlow"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: str = "development"

    database_url: str = "postgresql+asyncpg://jobflow:jobflow@localhost:5432/jobflow"
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str | None = None
    celery_result_backend: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def broker_url(self) -> str:
        """Return the configured Celery broker, defaulting to Redis."""

        return self.celery_broker_url or self.redis_url

    @property
    def result_backend(self) -> str:
        """Return the configured Celery result backend, defaulting to Redis."""

        return self.celery_result_backend or self.redis_url


@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings instance."""

    return Settings()


settings = get_settings()
