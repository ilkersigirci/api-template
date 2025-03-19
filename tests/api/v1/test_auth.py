import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from starlette import status


@pytest.mark.anyio
async def test_login(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    """Test login endpoint.

    Args:
        fastapi_app: current application fixture.
        client: client fixture.
    """
    url = fastapi_app.url_path_for("login_access_token")
    response = await client.post(
        url,
        data={"username": "john@example.com", "password": "password"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.anyio
async def test_login_incorrect_password(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    """Test login with incorrect password.

    Args:
        fastapi_app: current application fixture.
        client: client fixture.
    """
    url = fastapi_app.url_path_for("login_access_token")
    response = await client.post(
        url,
        data={"username": "john@example.com", "password": "wrong_password"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect email or password"


@pytest.mark.anyio
async def test_register_user(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    """Test user registration.

    Args:
        fastapi_app: current application fixture.
        client: client fixture.
    """
    url = fastapi_app.url_path_for("register_user")
    response = await client.post(
        url,
        json={
            "name": "Test User",
            "email": "test_user@example.com",
            "password": "test_password",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == "test_user@example.com"
    assert data["name"] == "Test User"
    assert "id" in data


@pytest.mark.anyio
async def test_register_existing_user(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    """Test registering with an email that's already in use.

    Args:
        fastapi_app: current application fixture.
        client: client fixture.
    """
    url = fastapi_app.url_path_for("register_user")
    response = await client.post(
        url,
        json={
            "name": "John Doe Clone",
            "email": "john@example.com",  # Already exists in repository
            "password": "test_password",
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "A user with this email already exists"


@pytest.mark.anyio
async def test_test_token(
    fastapi_app: FastAPI,
    client: AsyncClient,
    normal_user_token_headers,
) -> None:
    """Test the token test endpoint.

    Args:
        fastapi_app: current application fixture.
        client: client fixture.
        normal_user_token_headers: headers with normal user token.
    """
    url = fastapi_app.url_path_for("test_token")
    response = await client.post(url, headers=normal_user_token_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == 1
    assert data["email"] == "john@example.com"
    assert data["name"] == "John Doe"
