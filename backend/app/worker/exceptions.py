"""Explicit task error categories used by the retry policy."""
class RetryableJobError(RuntimeError):
    """A transient error that may be retried."""
class PermanentJobError(ValueError):
    """A validation or business error that must not be retried."""
