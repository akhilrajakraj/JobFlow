"""Worker monitoring endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import current_user, require_role
from app.core.database import get_db
from app.models.user import User
from app.schemas.worker import WorkerRegister, WorkerResponse
from app.services.worker_service import heartbeat_worker, list_workers, register_worker

router = APIRouter(prefix="/workers", tags=["workers"])

Session = Annotated[AsyncSession, Depends(get_db)]
AuthenticatedUser = Annotated[User, Depends(current_user)]
Operator = Annotated[User, Depends(require_role("ADMIN", "OPERATOR"))]


@router.post("/register", response_model=WorkerResponse)
async def register(data: WorkerRegister, session: Session, _: Operator) -> WorkerResponse:
    """Register or refresh a worker."""
    return await register_worker(session, data)


@router.post("/{worker_name}/heartbeat", response_model=WorkerResponse)
async def heartbeat(worker_name: str, session: Session, _: Operator) -> WorkerResponse:
    """Record a worker heartbeat."""
    worker = await heartbeat_worker(session, worker_name)
    if worker is None:
        raise HTTPException(status_code=404, detail="Worker not found")
    return worker


@router.get("", response_model=list[WorkerResponse])
async def workers(session: Session, _: AuthenticatedUser) -> list[WorkerResponse]:
    """Return registered workers and update stale statuses."""
    return await list_workers(session)
