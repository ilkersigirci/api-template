from typing import Any, AsyncGenerator

import pytest
from app.api.application import get_app
from app.api.auth.utils import create_access_token, get_password_hash
from app.api.items.models import ItemModel
from app.api.redis.deps import get_redis_pool
from app.api.users.models import UserModel
from app.api.users.schemas import User
from app.core.settings import settings
from app.db.deps import get_db_session
from app.db.meta import meta
from app.db.utils import create_database, drop_database, load_all_db_models
from fakeredis import FakeServer
from fakeredis.aioredis import FakeConnection
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from redis.asyncio import ConnectionPool
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


@pytest.fixture(scope="session")
def mock_users_data() -> list[dict[str, Any]]:
    """Provides mock user data."""
    return [
        {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "hashed_password": get_password_hash("password"),
        },
        {
            "id": 2,
            "name": "Jane Doe",
            "email": "jane@example.com",
            "hashed_password": get_password_hash("password"),
        },
        {
            "id": 3,
            "name": "admin",
            "email": "admin@mail.com",
            "hashed_password": get_password_hash("admin"),
        },
    ]


@pytest.fixture(scope="session")
def mock_items_data() -> list[dict[str, Any]]:
    """Provides mock item data."""
    return [
        {
            "id": 1,
            "name": "Item 1",
            "description": "Description for Item 1",
            "price": 10.5,
        },
        {
            "id": 2,
            "name": "Item 2",
            "description": "Description for Item 2",
            "price": 20.0,
        },
    ]


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Backend for anyio pytest plugin.

    Returns:
        Backend name
    """
    return "asyncio"


@pytest.fixture(scope="session")
async def _engine(
    mock_users_data: list[dict[str, Any]], mock_items_data: list[dict[str, Any]]
) -> AsyncGenerator[AsyncEngine, None]:
    """Create engine and databases.

    Args:
        mock_users_data: Fixture providing mock user data.
        mock_items_data: Fixture providing mock item data.

    Yields:
        New db engine.
    """

    load_all_db_models()

    await create_database()

    engine = create_async_engine(
        settings.DB_URL,
        # connect_args={"check_same_thread": True},
    )
    async with engine.begin() as conn:
        # Create tables
        await conn.run_sync(meta.create_all)

        # Insert mock data using fixtures
        await conn.execute(insert(UserModel), mock_users_data)
        await conn.execute(insert(ItemModel), mock_items_data)

    try:
        yield engine
    finally:
        await engine.dispose()
        await drop_database()


@pytest.fixture
async def dbsession(
    _engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """Get session to database.

    Fixture that returns a SQLAlchemy session with a SAVEPOINT, and the rollback to it
    after the test completes.

    Args:
        _engine: current engine.

    Yields:
        session: async session.
    """
    connection = await _engine.connect()
    trans = await connection.begin()

    session_maker = async_sessionmaker(
        connection,
        expire_on_commit=False,
    )
    session = session_maker()

    try:
        yield session
    finally:
        await session.close()
        await trans.rollback()
        await connection.close()


@pytest.fixture
async def fake_redis_pool() -> AsyncGenerator[ConnectionPool, None]:
    """Get instance of a fake redis.

    Yields:
        FakeRedis instance.
    """
    server = FakeServer()
    server.connected = True
    pool = ConnectionPool(connection_class=FakeConnection, server=server)

    yield pool

    await pool.disconnect()


@pytest.fixture
def fastapi_app(
    dbsession: AsyncSession,
    fake_redis_pool: ConnectionPool,
) -> FastAPI:
    """Fixture for creating FastAPI app.

    Returns:
        Fastapi app with mocked dependencies.
    """
    application = get_app()
    application.dependency_overrides[get_db_session] = lambda: dbsession
    application.dependency_overrides[get_redis_pool] = lambda: fake_redis_pool
    return application


@pytest.fixture
async def client(
    fastapi_app: FastAPI,
    anyio_backend: Any,
) -> AsyncGenerator[AsyncClient, None]:
    """Fixture that creates client for requesting server.

    Args:
        fastapi_app: the application.
        anyio_backend: backend for anyio pytest plugin.

    Yields:
        client for the app.
    """
    transport = ASGITransport(app=fastapi_app)

    async with AsyncClient(
        transport=transport, base_url="http://test", timeout=2.0
    ) as ac:
        yield ac


@pytest.fixture
def normal_user_token():
    """Create a token for a normal user.

    Returns:
        Access token for a normal user.
    """
    return create_access_token(subject="1")


@pytest.fixture
def normal_user_token_headers(normal_user_token):
    """Return authorization headers for normal user.

    Args:
        normal_user_token: Token for normal user.

    Returns:
        Authorization headers with the token.
    """
    return {"Authorization": f"Bearer {normal_user_token}"}


@pytest.fixture
def test_user():
    """Return a sample test user.

    Returns:
        User object representing a test user.
    """
    return User(id=1, name="John Doe", email="john@example.com")


@pytest.fixture
async def client_authenticated(
    fastapi_app: FastAPI,
    anyio_backend: Any,
    normal_user_token_headers,
) -> AsyncGenerator[AsyncClient, None]:
    """Fixture that creates client for requesting server with headers.

    Args:
        fastapi_app: the application.
        anyio_backend: backend for anyio pytest plugin.
        normal_user_token_headers: headers for normal user.

    Yields:
        client for the app.
    """
    transport = ASGITransport(app=fastapi_app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers=normal_user_token_headers,
        timeout=2.0,
    ) as ac:
        yield ac
