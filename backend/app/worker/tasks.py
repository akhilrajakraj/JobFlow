"""Celery execution and worker lifecycle tasks."""

import os
import time
import uuid
from datetime import datetime, timezone

from celery.exceptions import MaxRetriesExceededError, SoftTimeLimitExceeded
from celery.signals import worker_ready, worker_shutdown
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.metrics import active_jobs, job_duration, jobs_completed, jobs_retried
from app.models.job import Job, JobStatus
from app.models.job_attempt import JobAttempt
from app.models.worker import Worker
from app.services.job_state import transition
from app.worker.celery_app import celery_app
from app.worker.exceptions import PermanentJobError, RetryableJobError

sync_database_url = settings.database_url.replace("+asyncpg", "")
RETRY_BACKOFF_BASE = 5


def _engine():
    return create_engine(sync_database_url, pool_pre_ping=True)


def _worker_name() -> str:
    return f"{os.getenv('HOSTNAME', 'localhost')}@jobflow"


def _set_worker_status(name: str, status: str) -> None:
    engine = _engine()
    try:
        with Session(engine) as session:
            worker = session.scalar(select(Worker).where(Worker.worker_name == name))
            if worker:
                worker.status = status
                worker.last_heartbeat_at = datetime.now(timezone.utc)
                session.commit()
    finally:
        engine.dispose()


@worker_ready.connect
def register_celery_worker(sender=None, **_: object) -> None:
    """Register the worker using Celery's canonical hostname."""
    hostname = getattr(sender, "hostname", None) or _worker_name()
    engine = _engine()
    try:
        with Session(engine) as session:
            worker = session.scalar(select(Worker).where(Worker.worker_name == hostname))
            now = datetime.now(timezone.utc)
            if worker is None:
                session.add(Worker(worker_name=hostname, hostname=hostname, status="ONLINE", last_heartbeat_at=now))
            else:
                worker.status = "ONLINE"
                worker.last_heartbeat_at = now
            session.commit()
    finally:
        engine.dispose()


@worker_shutdown.connect
def mark_celery_worker_offline(sender=None, **_: object) -> None:
    """Mark the exact Celery worker hostname offline on graceful shutdown."""
    name = getattr(sender, "hostname", None) or _worker_name()
    _set_worker_status(name, "OFFLINE")


@celery_app.task(name="jobflow.health_check")
def health_check() -> str:
    return "ok"


def _execute(task_type: str, payload: dict) -> dict:
    if task_type == "echo":
        return {"echo": payload}
    if task_type == "sum":
        numbers = payload.get("numbers", [])
        if not isinstance(numbers, list) or not all(isinstance(number, (int, float)) for number in numbers):
            raise PermanentJobError("sum task requires payload.numbers to be a list of numbers")
        return {"sum": sum(numbers)}
    if task_type == "fail":
        raise RetryableJobError("Intentional transient failure for retry testing")
    return {"message": "Job executed", "task_type": task_type, "payload": payload}


def _latest_attempt(session: Session, job_id: uuid.UUID) -> JobAttempt | None:
    return session.scalar(
        select(JobAttempt)
        .where(JobAttempt.job_id == job_id)
        .order_by(JobAttempt.attempt_number.desc())
        .limit(1)
    )


@celery_app.task(bind=True, name="jobflow.execute_job", acks_late=True)
def execute_job(self, job_id: str) -> dict:
    """Execute a job with bounded retries, explicit error classes and timing."""
    parsed_id = uuid.UUID(job_id)
    engine = _engine()
    counted_active = False
    started = time.monotonic()

    try:
        with Session(engine) as session:
            job = session.get(Job, parsed_id)
            if job is None:
                raise ValueError(f"Job {job_id} does not exist")
            if job.status in {JobStatus.SUCCESS, JobStatus.CANCELLED}:
                return job.result or {}

            job.status = transition(job.status, JobStatus.RUNNING)
            job.started_at = job.started_at or datetime.now(timezone.utc)
            previous = session.scalar(
                select(JobAttempt.attempt_number)
                .where(JobAttempt.job_id == parsed_id)
                .order_by(JobAttempt.attempt_number.desc())
                .limit(1)
            )
            attempt = JobAttempt(job_id=parsed_id, attempt_number=(previous or 0) + 1)
            session.add(attempt)
            session.commit()
            active_jobs.inc()
            counted_active = True

            try:
                with job_duration.time():
                    result = _execute(job.task_type, job.payload)
            except SoftTimeLimitExceeded as exc:
                attempt.error = f"Job exceeded timeout of {job.timeout_seconds}s"
                attempt.completed_at = datetime.now(timezone.utc)
                job.error = attempt.error
                job.status = JobStatus.FAILED
                job.completed_at = datetime.now(timezone.utc)
                session.commit()
                jobs_completed.labels(status="FAILED").inc()
                raise exc
            except PermanentJobError as exc:
                attempt.error = str(exc)
                attempt.completed_at = datetime.now(timezone.utc)
                job.error = str(exc)
                job.status = JobStatus.FAILED
                job.completed_at = datetime.now(timezone.utc)
                session.commit()
                jobs_completed.labels(status="FAILED").inc()
                raise
            except RetryableJobError as exc:
                return _retry_or_fail(self, session, job, attempt, exc)
            except Exception as exc:
                # Unexpected infrastructure/application failures are transient by default.
                return _retry_or_fail(self, session, job, attempt, RetryableJobError(str(exc)))

            attempt.completed_at = datetime.now(timezone.utc)
            job.status = transition(job.status, JobStatus.SUCCESS)
            job.result = result
            job.error = None
            job.completed_at = datetime.now(timezone.utc)
            session.commit()
            jobs_completed.labels(status="SUCCESS").inc()
            return result
    except MaxRetriesExceededError:
        raise
    finally:
        if counted_active:
            active_jobs.dec()
        elapsed = time.monotonic() - started
        if elapsed < 0:
            raise RuntimeError("monotonic clock moved backwards")
        engine.dispose()


def _retry_or_fail(self, session: Session, job: Job, attempt: JobAttempt, exc: RetryableJobError) -> dict:
    attempt.error = str(exc)
    attempt.completed_at = datetime.now(timezone.utc)
    job.retry_count += 1
    job.error = str(exc)
    if job.retry_count <= job.max_retries:
        job.status = transition(job.status, JobStatus.RETRYING)
        session.commit()
        jobs_retried.inc()
        countdown = RETRY_BACKOFF_BASE * (2 ** (job.retry_count - 1))
        raise self.retry(exc=exc, countdown=countdown, max_retries=job.max_retries)
    job.status = transition(job.status, JobStatus.FAILED)
    job.completed_at = datetime.now(timezone.utc)
    session.commit()
    jobs_completed.labels(status="FAILED").inc()
    raise exc
