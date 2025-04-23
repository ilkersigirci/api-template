from typing import Annotated, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from taskiq import TaskiqDepends


async def get_db_session(
    request: Annotated[Request, TaskiqDepends()],
) -> AsyncGenerator[AsyncSession, None]:
    """Create and get database session.

    Args:
        request: current request.

    Yields:
        session: database session.
    """
    session: AsyncSession = request.app.state.db_session_factory()

    try:
        yield session
    finally:
        await session.commit()
        await session.close()
