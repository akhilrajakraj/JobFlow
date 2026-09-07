"""Job management endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.job import JobCreate, JobListResponse, JobResponse
from app.services.job_service import create_job, get_job, list_jobs

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def submit_job(data: JobCreate, session: AsyncSession = Depends(get_db)) -> JobResponse:
    """Create and asynchronously dispatch a job."""

    return await create_job(session, data)


@router.get("", response_model=JobListResponse)
async def get_jobs(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db),
) -> JobListResponse:
    """List submitted jobs."""

    items, total = await list_jobs(session, limit=limit, offset=offset)
    return JobListResponse(items=items, total=total)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job_by_id(job_id: uuid.UUID, session: AsyncSession = Depends(get_db)) -> JobResponse:
    """Return a job and its current lifecycle state."""

    job = await get_job(session, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
