"""Database session management and FastAPI dependency provider.

Configures the ``async_sessionmaker`` factory and exposes a
``get_session`` async generator that provides transactional database
sessions as FastAPI dependencies. Commits on success, rolls back on
any exception.
"""

from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.database.engine import async_engine
from src.conf import settings


AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autoflush=settings.AUTO_FLUSH,
    expire_on_commit=settings.EXPIRE_ON_COMMIT,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Provides a transactional database session as a FastAPI dependency.

    Creates an ``AsyncSession`` via the configured session factory.
    On successful completion of the request, the session is committed.
    On any exception, the session is rolled back and the exception is
    re-raised to propagate to the global error handler.

    Yields:
        AsyncSession: The active database session bound to the current request.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise