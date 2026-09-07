"""Worker registration and heartbeat business logic."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.metrics import registered_workers
from app.models.worker import Worker
from app.schemas.worker import WorkerRegister

HEARTBEAT_TIMEOUT_SECONDS = 60


async def register_worker(session: AsyncSession, data: WorkerRegister) -> Worker:
    worker = await session.scalar(select(Worker).where(Worker.worker_name == data.worker_name))
    now = datetime.now(timezone.utc)
    if worker is None:
        worker = Worker(worker_name=data.worker_name, hostname=data.hostname, concurrency=data.concurrency,
                        metadata=data.metadata, status="ONLINE", last_heartbeat_at=now)
        session.add(worker)
    else:
        worker.hostname, worker.concurrency, worker.metadata = data.hostname, data.concurrency, data.metadata
        worker.status, worker.last_heartbeat_at = "ONLINE", now
    await session.commit()
    await session.refresh(worker)
    return worker


async def heartbeat_worker(session: AsyncSession, worker_name: str) -> Worker | None:
    worker = await session.scalar(select(Worker).where(Worker.worker_name == worker_name))
    if worker is None:
        return None
    worker.status = "ONLINE"
    worker.last_heartbeat_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(worker)
    return worker


async def list_workers(session: AsyncSession) -> list[Worker]:
    result = await session.execute(select(Worker).order_by(Worker.registered_at.desc()))
    workers = list(result.scalars().all())
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=HEARTBEAT_TIMEOUT_SECONDS)
    for worker in workers:
        if worker.last_heartbeat_at < cutoff and worker.status == "ONLINE":
            worker.status = "STALE"
    await session.commit()
    registered_workers.set(len(workers))
    return workers
