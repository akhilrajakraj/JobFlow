"""Celery tasks for JobFlow."""
import os
import uuid
from datetime import datetime, timezone
from celery.exceptions import MaxRetriesExceededError, SoftTimeLimitExceeded
from celery.signals import worker_ready, worker_shutdown
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.metrics import active_jobs, jobs_completed, jobs_retried, job_duration
from app.models.job import Job, JobStatus
from app.models.job_attempt import JobAttempt
from app.models.worker import Worker
from app.worker.celery_app import celery_app
from app.worker.exceptions import PermanentJobError, RetryableJobError
sync_database_url = settings.database_url.replace("+asyncpg", "")
RETRY_BACKOFF_BASE = 5

def _engine(): return create_engine(sync_database_url, pool_pre_ping=True)
def _worker_name(): return f"{os.getenv('HOSTNAME', 'localhost')}@jobflow"

def _set_worker_status(name: str, status: str):
    engine = _engine()
    try:
        with Session(engine) as session:
            worker = session.scalar(select(Worker).where(Worker.worker_name == name))
            if worker: worker.status = status; worker.last_heartbeat_at = datetime.now(timezone.utc); session.commit()
    finally: engine.dispose()

@worker_ready.connect
def register_celery_worker(sender=None, **_):
    hostname = getattr(sender, "hostname", None) or _worker_name(); engine = _engine()
    try:
        with Session(engine) as session:
            worker = session.scalar(select(Worker).where(Worker.worker_name == hostname)); now = datetime.now(timezone.utc)
            if worker is None: session.add(Worker(worker_name=hostname, hostname=hostname, status="ONLINE", last_heartbeat_at=now))
            else: worker.status = "ONLINE"; worker.last_heartbeat_at = now
            session.commit()
    finally: engine.dispose()

@worker_shutdown.connect
def mark_celery_worker_offline(**_): _set_worker_status(_worker_name(), "OFFLINE")

@celery_app.task(name="jobflow.health_check")
def health_check(): return "ok"

@celery_app.task(bind=True, name="jobflow.execute_job", acks_late=True)
def execute_job(self, job_id: str) -> dict:
    parsed_id = uuid.UUID(job_id); engine = _engine(); counted_active = False
    started_monotonic = None
    try:
        with Session(engine) as session:
            job = session.get(Job, parsed_id)
            if job is None: raise ValueError(f"Job {job_id} does not exist")
            if job.status in {JobStatus.SUCCESS, JobStatus.CANCELLED}: return job.result or {}
            job.status = JobStatus.RUNNING; job.started_at = job.started_at or datetime.now(timezone.utc)
            attempt_number = (session.scalar(select(JobAttempt.attempt_number).where(JobAttempt.job_id == parsed_id).order_by(JobAttempt.attempt_number.desc()).limit(1)) or 0) + 1
            session.add(JobAttempt(job_id=parsed_id, attempt_number=attempt_number)); session.commit(); active_jobs.inc(); counted_active = True
            try:
                with job_duration.time():
                    if job.task_type == "echo": result = {"echo": job.payload}
                    elif job.task_type == "sum":
                        numbers = job.payload.get("numbers", [])
                        if not isinstance(numbers, list) or not all(isinstance(n, (int, float)) for n in numbers): raise PermanentJobError("sum task requires payload.numbers to be a list of numbers")
                        result = {"sum": sum(numbers)}
                    elif job.task_type == "fail": raise RetryableJobError("Intentional transient failure for retry testing")
                    else: result = {"message": "Job executed", "task_type": job.task_type, "payload": job.payload}
            except SoftTimeLimitExceeded as exc:
                attempt = session.scalar(select(JobAttempt).where(JobAttempt.job_id == parsed_id).order_by(JobAttempt.attempt_number.desc()).limit(1))
                if attempt: attempt.error = "Job exceeded timeout"; attempt.completed_at = datetime.now(timezone.utc)
                job.status = JobStatus.FAILED; job.error = "Job exceeded timeout"; job.completed_at = datetime.now(timezone.utc); session.commit(); jobs_completed.labels(status="FAILED").inc(); raise
            except RetryableJobError as exc:
                attempt = session.scalar(select(JobAttempt).where(JobAttempt.job_id == parsed_id).order_by(JobAttempt.attempt_number.desc()).limit(1))
                if attempt: attempt.error = str(exc); attempt.completed_at = datetime.now(timezone.utc)
                job.retry_count += 1; job.error = str(exc)
                if job.retry_count <= job.max_retries:
                    job.status = JobStatus.RETRYING; session.commit(); jobs_retried.inc(); countdown = RETRY_BACKOFF_BASE * (2 ** (job.retry_count - 1)); raise self.retry(exc=exc, countdown=countdown, max_retries=job.max_retries)
                job.status = JobStatus.FAILED; job.completed_at = datetime.now(timezone.utc); session.commit(); jobs_completed.labels(status="FAILED").inc(); raise
            except PermanentJobError as exc:
                attempt = session.scalar(select(JobAttempt).where(JobAttempt.job_id == parsed_id).order_by(JobAttempt.attempt_number.desc()).limit(1))
                if attempt: attempt.error = str(exc); attempt.completed_at = datetime.now(timezone.utc)
                job.error = str(exc); job.status = JobStatus.FAILED; job.completed_at = datetime.now(timezone.utc); session.commit(); jobs_completed.labels(status="FAILED").inc(); raise
            attempt = session.scalar(select(JobAttempt).where(JobAttempt.job_id == parsed_id).order_by(JobAttempt.attempt_number.desc()).limit(1))
            if attempt: attempt.completed_at = datetime.now(timezone.utc)
            job.status = JobStatus.SUCCESS; job.result = result; job.error = None; job.completed_at = datetime.now(timezone.utc); session.commit(); jobs_completed.labels(status="SUCCESS").inc(); return result
    except MaxRetriesExceededError:
        raise
    finally:
        if counted_active: active_jobs.dec()
        engine.dispose()
