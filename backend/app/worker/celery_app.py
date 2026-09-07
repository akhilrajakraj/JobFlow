"""Celery application configuration."""

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "jobflow",
    broker=settings.broker_url,
    backend=settings.result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    task_default_priority=5,
    task_queue_max_priority=10,
    broker_transport_options={"priority_steps": list(range(10))},
    task_soft_time_limit=3600,
    task_time_limit=3660,
)
