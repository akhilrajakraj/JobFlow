"""Application configuration and production safety checks."""

from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables and .env."""

    app_name: str = "JobFlow"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    database_url: str = "postgresql+asyncpg://jobflow:jobflow@localhost:5432/jobflow"
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str | None = None
    celery_result_backend: str | None = None
    jwt_secret: str = "change-me-in-production"
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    admin_username: str = "admin"
    admin_password: str = "change-me-now"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    @model_validator(mode="after")
    def validate_security(self) -> "Settings":
        if self.environment.lower() in {"production", "prod"}:
            if self.jwt_secret in {"", "change-me-in-production"} or len(self.jwt_secret) < 32:
                raise ValueError("Production JWT_SECRET must be at least 32 characters")
            if self.admin_password in {"", "change-me-now"} or len(self.admin_password) < 12:
                raise ValueError("Production ADMIN_PASSWORD must be at least 12 characters")
            if self.debug:
                raise ValueError("DEBUG must be false in production")
        return self

    @property
    def broker_url(self) -> str:
        return self.celery_broker_url or self.redis_url

    @property
    def result_backend(self) -> str:
        return self.celery_result_backend or self.redis_url

    @property
    def allowed_origins(self) -> list[str]:
        return [value.strip() for value in self.cors_origins.split(",") if value.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
