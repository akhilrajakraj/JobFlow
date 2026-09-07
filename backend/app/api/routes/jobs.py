"""Job management endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import current_user, require_role
from app.core.database import get_db
from app.models.job import JobStatus
from app.models.user import User
from app.schemas.job import JobCreate, JobListResponse, JobResponse
from app.services.job_service import IdempotencyConflictError, cancel_job, create_job, get_job, list_jobs

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def submit_job(
    data: JobCreate,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("ADMIN", "OPERATOR")),
) -> JobResponse:
    try:
        return await create_job(session, data)
    except IdempotencyConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("", response_model=JobListResponse)
async def get_jobs(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db),
    _: User = Depends(current_user),
) -> JobListResponse:
    items, total = await list_jobs(session, limit=limit, offset=offset)
    return JobListResponse(items=items, total=total)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job_by_id(
    job_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(current_user),
) -> JobResponse:
    job = await get_job(session, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/{job_id}/cancel", response_model=JobResponse)
async def cancel(
    job_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("ADMIN", "OPERATOR")),
) -> JobResponse:
    job = await get_job(session, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status in {JobStatus.SUCCESS, JobStatus.FAILED, JobStatus.CANCELLED}:
        raise HTTPException(status_code=409, detail="Job is already in a terminal state")
    return await cancel_job(session, job_id)
