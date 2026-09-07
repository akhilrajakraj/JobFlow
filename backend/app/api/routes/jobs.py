"""Job management endpoints."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import current_user, require_role
from app.core.database import get_db
from app.models.job import JobStatus
from app.models.user import User
from app.schemas.job import JobCreate, JobListResponse, JobResponse
from app.services.job_service import (
    IdempotencyConflictError,
    cancel_job,
    create_job,
    get_job,
    list_jobs,
)

router = APIRouter(prefix="/jobs", tags=["jobs"])

Session = Annotated[AsyncSession, Depends(get_db)]
AuthenticatedUser = Annotated[User, Depends(current_user)]
Operator = Annotated[User, Depends(require_role("ADMIN", "OPERATOR"))]
IdempotencyHeader = Annotated[str | None, Header(alias="Idempotency-Key")]


@router.post("", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def submit_job(
    data: JobCreate,
    session: Session,
    _: Operator,
    idempotency_key: IdempotencyHeader,
) -> JobResponse:
    """Submit a background job for asynchronous execution."""
    if idempotency_key:
        if data.idempotency_key and data.idempotency_key != idempotency_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Body and Idempotency-Key header do not match",
            )
        data = data.model_copy(update={"idempotency_key": idempotency_key})
    try:
        return await create_job(session, data)
    except IdempotencyConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get("", response_model=JobListResponse)
async def get_jobs(
    session: Session,
    _: AuthenticatedUser,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> JobListResponse:
    """Return a paginated list of jobs."""
    items, total = await list_jobs(session, limit=limit, offset=offset)
    return JobListResponse(items=items, total=total)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job_by_id(
    job_id: uuid.UUID,
    session: Session,
    _: AuthenticatedUser,
) -> JobResponse:
    """Return a single job by ID."""
    job = await get_job(session, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/{job_id}/cancel", response_model=JobResponse)
async def cancel(
    job_id: uuid.UUID,
    session: Session,
    _: Operator,
) -> JobResponse:
    """Cancel a non-terminal job."""
    job = await get_job(session, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status in {JobStatus.SUCCESS, JobStatus.FAILED, JobStatus.CANCELLED}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Job is already in a terminal state",
        )
    return await cancel_job(session, job_id)
