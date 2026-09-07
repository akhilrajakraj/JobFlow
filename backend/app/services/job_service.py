"""Job business logic."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job, JobStatus
from app.schemas.job import JobCreate
from app.worker.tasks import execute_job


async def create_job(session: AsyncSession, data: JobCreate) -> Job:
    """Persist a queued job and enqueue its Celery task."""

    job = Job(task_type=data.task_type, payload=data.payload, status=JobStatus.QUEUED)
    session.add(job)
    await session.commit()
    await session.refresh(job)

    task = execute_job.delay(str(job.id))
    job.celery_task_id = task.id
    await session.commit()
    await session.refresh(job)
    return job


async def get_job(session: AsyncSession, job_id: uuid.UUID) -> Job | None:
    """Return a job by ID."""

    return await session.get(Job, job_id)


async def list_jobs(session: AsyncSession, limit: int = 50, offset: int = 0) -> tuple[list[Job], int]:
    """Return jobs ordered newest-first with a total count."""

    items_result = await session.execute(
        select(Job).order_by(Job.created_at.desc()).limit(limit).offset(offset)
    )
    total = await session.scalar(select(func.count()).select_from(Job))
    return list(items_result.scalars().all()), int(total or 0)
