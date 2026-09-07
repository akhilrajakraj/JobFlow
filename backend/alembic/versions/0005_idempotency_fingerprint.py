"""Persist idempotency request fingerprints."""

from alembic import op
import sqlalchemy as sa

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("jobs", sa.Column("request_hash", sa.String(64), nullable=True))
    op.create_index("ix_jobs_request_hash", "jobs", ["request_hash"])


def downgrade() -> None:
    op.drop_index("ix_jobs_request_hash", table_name="jobs")
    op.drop_column("jobs", "request_hash")
