"""ORM model registry for database initialization."""

from app.models.job import Base
from app.models.job_attempt import JobAttempt

__all__ = ["Base", "JobAttempt"]
