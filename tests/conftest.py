from typing import Any, AsyncGenerator

import pytest
from app.api.application import get_app
from app.core.security import create_access_token
from app.dependencies.redis import get_redis_pool
from app.models.user import User
from fakeredis import FakeServer
from fakeredis.aioredis import FakeConnection
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from redis.asyncio import ConnectionPool


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Backend for anyio pytest plugin.

    Returns:
        Backend name
    """
    return "asyncio"


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
    fake_redis_pool: ConnectionPool,
) -> FastAPI:
    """Fixture for creating FastAPI app.

    Returns:
        Fastapi app with mocked dependencies.
    """
    application = get_app()
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
