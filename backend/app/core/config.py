"""Application configuration."""
from functools import lru_cache
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    app_name: str = "JobFlow"; app_version: str = "0.1.0"; debug: bool = False; environment: str = "development"
    database_url: str = "postgresql+asyncpg://jobflow:jobflow@localhost:5432/jobflow"; redis_url: str = "redis://localhost:6379/0"; celery_broker_url: str | None = None; celery_result_backend: str | None = None
    jwt_secret: str = "change-me-in-production"; cors_origins: str = "http://localhost:3000,http://localhost:5173"; admin_username: str = "admin"; admin_password: str = "change-me-now"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")
    @model_validator(mode="after")
    def validate_security(self):
        if self.environment.lower() in {"production", "prod"} and (self.jwt_secret == "change-me-in-production" or self.admin_password == "change-me-now"): raise ValueError("Production requires JWT_SECRET and ADMIN_PASSWORD to be changed")
        return self
    @property
    def broker_url(self): return self.celery_broker_url or self.redis_url
    @property
    def result_backend(self): return self.celery_result_backend or self.redis_url
    @property
    def allowed_origins(self): return [x.strip() for x in self.cors_origins.split(",") if x.strip()]
@lru_cache
def get_settings(): return Settings()
settings = get_settings()
