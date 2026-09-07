"""Idempotency contract tests."""

from app.schemas.job import JobCreate
from app.services.job_service import request_fingerprint


def test_fingerprint_is_deterministic_for_equivalent_json() -> None:
    first = JobCreate(task_type="sum", payload={"numbers": [1, 2]}, idempotency_key="abc")
    second = JobCreate(task_type="sum", payload={"numbers": [1, 2]}, idempotency_key="abc")
    assert request_fingerprint(first) == request_fingerprint(second)


def test_fingerprint_changes_when_request_changes() -> None:
    first = JobCreate(task_type="sum", payload={"numbers": [1, 2]}, idempotency_key="abc")
    second = JobCreate(task_type="sum", payload={"numbers": [1, 3]}, idempotency_key="abc")
    assert request_fingerprint(first) != request_fingerprint(second)
