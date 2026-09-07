"""Create jobs and job attempts tables."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

job_status = postgresql.ENUM("QUEUED", "RUNNING", "SUCCESS", "FAILED", "RETRYING", "CANCELLED", name="job_status")


def upgrade() -> None:
    bind = op.get_bind()
    job_status.create(bind, checkfirst=True)
    op.create_table(
        "jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("task_type", sa.String(100), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("status", job_status, nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("max_retries", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("timeout_seconds", sa.Integer(), nullable=False, server_default="300"),
        sa.Column("idempotency_key", sa.String(255), unique=True),
        sa.Column("result", sa.JSON()),
        sa.Column("error", sa.Text()),
        sa.Column("celery_task_id", sa.String(255), unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_jobs_status_created_at", "jobs", ["status", "created_at"])
    op.create_index("ix_jobs_priority_created_at", "jobs", ["priority", "created_at"])
    op.create_table(
        "job_attempts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("attempt_number", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("error", sa.Text()),
    )
    op.create_index("ix_job_attempts_job_id", "job_attempts", ["job_id"])


def downgrade() -> None:
    op.drop_index("ix_job_attempts_job_id", table_name="job_attempts")
    op.drop_table("job_attempts")
    op.drop_index("ix_jobs_priority_created_at", table_name="jobs")
    op.drop_index("ix_jobs_status_created_at", table_name="jobs")
    op.drop_table("jobs")
    job_status.drop(op.get_bind(), checkfirst=True)
