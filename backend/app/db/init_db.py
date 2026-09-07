"""Development database initialization."""

from app.core.database import engine
from app.db.base import Base


async def init_db() -> None:
    """Create ORM tables for local development.

    Migrations will replace this initializer when Alembic is introduced.
    """

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
