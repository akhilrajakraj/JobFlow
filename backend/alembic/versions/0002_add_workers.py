"""Add worker registry table."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "workers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("worker_name", sa.String(255), nullable=False, unique=True),
        sa.Column("hostname", sa.String(255), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="ONLINE"),
        sa.Column("concurrency", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("active_tasks", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("registered_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("last_heartbeat_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_workers_status_heartbeat", "workers", ["status", "last_heartbeat_at"])


def downgrade() -> None:
    op.drop_index("ix_workers_status_heartbeat", table_name="workers")
    op.drop_table("workers")
