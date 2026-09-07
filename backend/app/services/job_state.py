"""Centralized job lifecycle rules."""

from app.models.job import JobStatus

_ALLOWED: dict[JobStatus, frozenset[JobStatus]] = {
    JobStatus.QUEUED: frozenset({JobStatus.RUNNING, JobStatus.CANCELLED}),
    JobStatus.RUNNING: frozenset(
        {
            JobStatus.SUCCESS,
            JobStatus.RETRYING,
            JobStatus.FAILED,
            JobStatus.CANCELLED,
        }
    ),
    JobStatus.RETRYING: frozenset({JobStatus.RUNNING, JobStatus.CANCELLED}),
    JobStatus.SUCCESS: frozenset(),
    JobStatus.FAILED: frozenset(),
    JobStatus.CANCELLED: frozenset(),
}


def can_transition(current: JobStatus, target: JobStatus) -> bool:
    """Return whether a lifecycle transition is valid."""
    return target in _ALLOWED[current]


def transition(current: JobStatus, target: JobStatus) -> JobStatus:
    """Validate and return a new job state."""
    if not can_transition(current, target):
        raise ValueError(f"Invalid job transition: {current.value} -> {target.value}")
    return target
