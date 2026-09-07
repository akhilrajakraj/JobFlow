"""Add hardening constraints and indexes."""

from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint("uq_job_attempt_number", "job_attempts", ["job_id", "attempt_number"])
    op.create_index("ix_jobs_idempotency_key", "jobs", ["idempotency_key"], unique=True)
    op.create_index("ix_jobs_status_priority_created", "jobs", ["status", "priority", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_jobs_status_priority_created", table_name="jobs")
    op.drop_index("ix_jobs_idempotency_key", table_name="jobs")
    op.drop_constraint("uq_job_attempt_number", "job_attempts", type_="unique")
