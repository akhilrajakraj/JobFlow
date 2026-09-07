"""Worker registration and heartbeat business logic."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.worker import Worker
from app.schemas.worker import WorkerRegister


async def register_worker(session: AsyncSession, data: WorkerRegister) -> Worker:
    """Create or refresh a worker registration."""

    worker = await session.scalar(select(Worker).where(Worker.worker_name == data.worker_name))
    now = datetime.now(timezone.utc)
    if worker is None:
        worker = Worker(
            worker_name=data.worker_name,
            hostname=data.hostname,
            concurrency=data.concurrency,
            metadata=data.metadata,
            status="ONLINE",
            last_heartbeat_at=now,
        )
        session.add(worker)
    else:
        worker.hostname = data.hostname
        worker.concurrency = data.concurrency
        worker.metadata = data.metadata
        worker.status = "ONLINE"
        worker.last_heartbeat_at = now
    await session.commit()
    await session.refresh(worker)
    return worker


async def heartbeat_worker(session: AsyncSession, worker_name: str) -> Worker | None:
    """Refresh a worker heartbeat."""

    worker = await session.scalar(select(Worker).where(Worker.worker_name == worker_name))
    if worker is None:
        return None
    worker.status = "ONLINE"
    worker.last_heartbeat_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(worker)
    return worker


async def list_workers(session: AsyncSession) -> list[Worker]:
    """Return workers ordered by registration time."""

    result = await session.execute(select(Worker).order_by(Worker.registered_at.desc()))
    return list(result.scalars().all())
