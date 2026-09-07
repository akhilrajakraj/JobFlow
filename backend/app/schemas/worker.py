"""Worker API schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WorkerRegister(BaseModel):
    worker_name: str = Field(min_length=1, max_length=255)
    hostname: str = Field(min_length=1, max_length=255)
    concurrency: int = Field(default=1, ge=1, le=1000)
    metadata: dict = Field(default_factory=dict)


class WorkerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    worker_name: str
    hostname: str
    status: str
    concurrency: int
    active_tasks: int
    metadata: dict
    registered_at: datetime
    last_heartbeat_at: datetime
