"""Job lifecycle state-machine tests."""

import pytest

from app.models.job import JobStatus
from app.services.job_state import can_transition, transition


def test_valid_transitions() -> None:
    assert can_transition(JobStatus.QUEUED, JobStatus.RUNNING)
    assert can_transition(JobStatus.RUNNING, JobStatus.RETRYING)
    assert can_transition(JobStatus.RETRYING, JobStatus.RUNNING)
    assert can_transition(JobStatus.RUNNING, JobStatus.SUCCESS)
    assert can_transition(JobStatus.RUNNING, JobStatus.FAILED)
    assert can_transition(JobStatus.QUEUED, JobStatus.CANCELLED)


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (JobStatus.SUCCESS, JobStatus.RUNNING),
        (JobStatus.FAILED, JobStatus.RETRYING),
        (JobStatus.CANCELLED, JobStatus.SUCCESS),
        (JobStatus.QUEUED, JobStatus.SUCCESS),
    ],
)
def test_terminal_and_invalid_transitions_are_rejected(current: JobStatus, target: JobStatus) -> None:
    with pytest.raises(ValueError, match="Invalid job transition"):
        transition(current, target)
