"""Celery tasks for JobFlow."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.job import Job, JobStatus
from app.models.job_attempt import JobAttempt
from app.worker.celery_app import celery_app


sync_database_url = settings.database_url.replace("+asyncpg", "")


def _update_job(job_id: uuid.UUID, status: JobStatus, **values: object) -> None:
    """Update a job from the synchronous Celery worker process."""

    engine = create_engine(sync_database_url, pool_pre_ping=True)
    try:
        with Session(engine) as session:
            job = session.get(Job, job_id)
            if job is None:
                return
            job.status = status
            for key, value in values.items():
                setattr(job, key, value)
            session.commit()
    finally:
        engine.dispose()


@celery_app.task(name="jobflow.health_check")
def health_check() -> str:
    """Simple task used to verify worker connectivity."""

    return "ok"


@celery_app.task(bind=True, name="jobflow.execute_job")
def execute_job(self, job_id: str) -> dict:
    """Execute a submitted job and persist its outcome."""

    parsed_id = uuid.UUID(job_id)
    engine = create_engine(sync_database_url, pool_pre_ping=True)

    try:
        with Session(engine) as session:
            job = session.get(Job, parsed_id)
            if job is None:
                raise ValueError(f"Job {job_id} does not exist")

            job.status = JobStatus.RUNNING
            job.started_at = datetime.now(timezone.utc)
            attempt_count = session.scalar(
                select(JobAttempt).where(JobAttempt.job_id == parsed_id)
            )
            attempt_number = 1 if attempt_count is None else 2
            session.add(JobAttempt(job_id=parsed_id, attempt_number=attempt_number))
            session.commit()

            # Phase 2 intentionally provides a deterministic demo executor.
            # Real task handlers will be introduced after the lifecycle is stable.
            if job.task_type == "echo":
                result = {"echo": job.payload}
            elif job.task_type == "sum":
                numbers = job.payload.get("numbers", [])
                if not isinstance(numbers, list) or not all(isinstance(n, (int, float)) for n in numbers):
                    raise ValueError("sum task requires payload.numbers to be a list of numbers")
                result = {"sum": sum(numbers)}
            else:
                result = {"message": "Job executed", "task_type": job.task_type, "payload": job.payload}

            now = datetime.now(timezone.utc)
            job.status = JobStatus.SUCCESS
            job.result = result
            job.completed_at = now
            session.commit()
            return result

    except Exception as exc:
        _update_job(parsed_id, JobStatus.FAILED, error=str(exc), completed_at=datetime.now(timezone.utc))
        raise
    finally:
        engine.dispose()
