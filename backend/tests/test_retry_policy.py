from app.worker.exceptions import PermanentJobError, RetryableJobError

def test_error_categories_are_distinct():
    assert issubclass(RetryableJobError, RuntimeError)
    assert issubclass(PermanentJobError, ValueError)
