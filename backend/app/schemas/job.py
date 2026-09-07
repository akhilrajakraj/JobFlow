"""Job API schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.job import JobStatus


class JobCreate(BaseModel):
    """Payload used to submit a job."""

    task_type: str = Field(min_length=1, max_length=100)
    payload: dict = Field(default_factory=dict)
    priority: int = Field(default=5, ge=1, le=10)
    max_retries: int = Field(default=3, ge=0, le=10)
    timeout_seconds: int = Field(default=300, ge=1, le=3600)
    idempotency_key: str | None = Field(default=None, min_length=1, max_length=255)


class JobResponse(BaseModel):
    """Public representation of a job."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    task_type: str
    payload: dict
    status: JobStatus
    priority: int
    max_retries: int
    retry_count: int
    timeout_seconds: int
    idempotency_key: str | None
    result: dict | None
    error: str | None
    celery_task_id: str | None
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None


class JobListResponse(BaseModel):
    """Paginated job listing response."""

    items: list[JobResponse]
    total: int
