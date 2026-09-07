"""Worker monitoring endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.worker import WorkerRegister, WorkerResponse
from app.services.worker_service import heartbeat_worker, list_workers, register_worker

router = APIRouter(prefix="/workers", tags=["workers"])


@router.post("/register", response_model=WorkerResponse)
async def register(data: WorkerRegister, session: AsyncSession = Depends(get_db)) -> WorkerResponse:
    return await register_worker(session, data)


@router.post("/{worker_name}/heartbeat", response_model=WorkerResponse)
async def heartbeat(worker_name: str, session: AsyncSession = Depends(get_db)) -> WorkerResponse:
    worker = await heartbeat_worker(session, worker_name)
    if worker is None:
        raise HTTPException(status_code=404, detail="Worker not found")
    return worker


@router.get("", response_model=list[WorkerResponse])
async def workers(session: AsyncSession = Depends(get_db)) -> list[WorkerResponse]:
    return await list_workers(session)
