"""Job persistence model."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Index, JSON, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for JobFlow ORM models."""


class JobStatus(str, enum.Enum):
    """Persisted lifecycle states for a job."""

    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    RETRYING = "RETRYING"
    CANCELLED = "CANCELLED"


class Job(Base):
    """A submitted asynchronous workload."""

    __tablename__ = "jobs"
    __table_args__ = (
        Index("ix_jobs_status_created_at", "status", "created_at"),
        Index("ix_jobs_priority_created_at", "priority", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_type: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, name="job_status"), nullable=False, default=JobStatus.QUEUED
    )
    priority: Mapped[int] = mapped_column(default=5, nullable=False)
    max_retries: Mapped[int] = mapped_column(default=3, nullable=False)
    retry_count: Mapped[int] = mapped_column(default=0, nullable=False)
    timeout_seconds: Mapped[int] = mapped_column(default=300, nullable=False)
    idempotency_key: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    celery_task_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
