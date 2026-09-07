"""Job API schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.job import JobStatus


class JobCreate(BaseModel):
    """Payload used to submit a job."""

    task_type: str = Field(min_length=1, max_length=100)
    payload: dict = Field(default_factory=dict)


class JobResponse(BaseModel):
    """Public representation of a job."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    task_type: str
    payload: dict
    status: JobStatus
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
