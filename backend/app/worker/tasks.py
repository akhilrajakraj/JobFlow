"""Celery tasks for JobFlow."""

from app.worker.celery_app import celery_app


@celery_app.task(name="jobflow.health_check")
def health_check() -> str:
    """Simple task used to verify worker connectivity."""

    return "ok"
