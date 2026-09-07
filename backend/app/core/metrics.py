"""Prometheus metrics for JobFlow."""

from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

jobs_submitted = Counter("jobflow_jobs_submitted_total", "Jobs submitted")
jobs_completed = Counter("jobflow_jobs_completed_total", "Jobs completed", ["status"])
jobs_retried = Counter("jobflow_jobs_retried_total", "Jobs retried")
active_jobs = Gauge("jobflow_active_jobs", "Jobs currently running")
registered_workers = Gauge("jobflow_registered_workers", "Registered workers")
job_duration = Histogram("jobflow_job_duration_seconds", "Job execution duration")


def metrics_response() -> tuple[bytes, str]:
    """Return the current Prometheus exposition payload."""
    return generate_latest(), CONTENT_TYPE_LATEST
