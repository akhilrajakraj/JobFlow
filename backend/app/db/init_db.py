"""Legacy development database initializer."""

from app.core.database import engine
from app.db.base import Base


async def init_db() -> None:
    """Create ORM tables for development when migrations are not used.

    Production and containerized environments should prefer Alembic migrations.
    """
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
