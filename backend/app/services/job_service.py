"""Job business logic."""
import uuid
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.metrics import jobs_submitted
from app.models.job import Job, JobStatus
from app.schemas.job import JobCreate
from app.worker.celery_app import celery_app
from app.worker.tasks import execute_job

async def create_job(session: AsyncSession, data: JobCreate) -> Job:
    if data.idempotency_key:
        existing = await session.scalar(select(Job).where(Job.idempotency_key == data.idempotency_key))
        if existing:
            if existing.celery_task_id is None and existing.status == JobStatus.QUEUED:
                task = execute_job.apply_async(args=[str(existing.id)], priority=data.priority, soft_time_limit=data.timeout_seconds, time_limit=data.timeout_seconds + 5)
                existing.celery_task_id = task.id; await session.commit(); await session.refresh(existing)
            return existing
    job = Job(task_type=data.task_type, payload=data.payload, status=JobStatus.QUEUED, priority=data.priority, max_retries=data.max_retries, timeout_seconds=data.timeout_seconds, idempotency_key=data.idempotency_key)
    session.add(job)
    try: await session.commit()
    except IntegrityError:
        await session.rollback()
        if data.idempotency_key:
            existing = await session.scalar(select(Job).where(Job.idempotency_key == data.idempotency_key))
            if existing: return existing
        raise
    await session.refresh(job)
    task = execute_job.apply_async(args=[str(job.id)], priority=data.priority, soft_time_limit=data.timeout_seconds, time_limit=data.timeout_seconds + 5)
    job.celery_task_id = task.id; await session.commit(); await session.refresh(job); jobs_submitted.inc(); return job

async def get_job(session: AsyncSession, job_id: uuid.UUID) -> Job | None: return await session.get(Job, job_id)

async def list_jobs(session: AsyncSession, limit: int = 50, offset: int = 0):
    result = await session.execute(select(Job).order_by(Job.priority.desc(), Job.created_at.desc()).limit(limit).offset(offset)); total = await session.scalar(select(func.count()).select_from(Job)); return list(result.scalars().all()), int(total or 0)

async def cancel_job(session: AsyncSession, job_id: uuid.UUID) -> Job | None:
    job = await session.get(Job, job_id)
    if job is None: return None
    if job.status in {JobStatus.SUCCESS, JobStatus.FAILED, JobStatus.CANCELLED}: return job
    if job.celery_task_id: celery_app.control.revoke(job.celery_task_id, terminate=True)
    job.status = JobStatus.CANCELLED; await session.commit(); await session.refresh(job); return job
