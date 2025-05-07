import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from starlette import status


@pytest.mark.anyio
async def test_get_users(
    fastapi_app: FastAPI,
    client: AsyncClient,
    normal_user_token_headers,
) -> None:
    """Test getting all users.

    Args:
        fastapi_app: current application fixture.
        client: client fixture.
        normal_user_token_headers: headers with normal user token.
    """
    url = fastapi_app.url_path_for("get_users")
    response = await client.get(url, headers=normal_user_token_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data)  # At least the one initial user should be present
    assert all("id" in user for user in data)
    assert all("email" in user for user in data)
    assert all("name" in user for user in data)


@pytest.mark.anyio
async def test_get_current_user(
    fastapi_app: FastAPI,
    client: AsyncClient,
    normal_user_token_headers,
) -> None:
    """Test getting the current user.

    Args:
        fastapi_app: current application fixture.
        client: client fixture.
        normal_user_token_headers: headers with normal user token.
    """
    url = fastapi_app.url_path_for("get_current_user_info")
    response = await client.get(url, headers=normal_user_token_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == 1
    assert data["email"] == "john@example.com"
    assert data["name"] == "John Doe"


@pytest.mark.anyio
async def test_get_specific_user(
    fastapi_app: FastAPI,
    client: AsyncClient,
    normal_user_token_headers,
) -> None:
    """Test getting a specific user by ID.

    Args:
        fastapi_app: current application fixture.
        client: client fixture.
        normal_user_token_headers: headers with normal user token.
    """
    url = fastapi_app.url_path_for("get_user", user_id=2)
    response = await client.get(url, headers=normal_user_token_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == 2
    assert data["email"] == "jane@example.com"
    assert data["name"] == "Jane Doe"


@pytest.mark.anyio
async def test_get_nonexistent_user(
    fastapi_app: FastAPI,
    client: AsyncClient,
    normal_user_token_headers,
) -> None:
    """Test getting a user that doesn't exist.

    Args:
        fastapi_app: current application fixture.
        client: client fixture.
        normal_user_token_headers: headers with normal user token.
    """
    url = fastapi_app.url_path_for("get_user", user_id=999)
    response = await client.get(url, headers=normal_user_token_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "User with id 999 not found"


@pytest.mark.anyio
async def test_create_user(
    fastapi_app: FastAPI,
    client: AsyncClient,
    normal_user_token_headers,
) -> None:
    """Test creating a new user.

    Args:
        fastapi_app: current application fixture.
        client: client fixture.
        normal_user_token_headers: headers with normal user token.
    """
    url = fastapi_app.url_path_for("create_user")
    response = await client.post(
        url,
        headers=normal_user_token_headers,
        json={
            "name": "Created User",
            "email": "created@example.com",
            "password": "created_password",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Created User"
    assert data["email"] == "created@example.com"
    assert "id" in data


@pytest.mark.anyio
async def test_update_user(
    fastapi_app: FastAPI,
    client: AsyncClient,
    normal_user_token_headers,
) -> None:
    """Test updating a user.

    Args:
        fastapi_app: current application fixture.
        client: client fixture.
        normal_user_token_headers: headers with normal user token.
    """
    url = fastapi_app.url_path_for("update_user", user_id=2)
    response = await client.put(
        url,
        headers=normal_user_token_headers,
        json={"name": "Updated Jane", "email": "updated_jane@example.com"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == 2
    assert data["name"] == "Updated Jane"
    assert data["email"] == "updated_jane@example.com"


@pytest.mark.anyio
async def test_update_nonexistent_user(
    fastapi_app: FastAPI,
    client: AsyncClient,
    normal_user_token_headers,
) -> None:
    """Test updating a user that doesn't exist.

    Args:
        fastapi_app: current application fixture.
        client: client fixture.
        normal_user_token_headers: headers with normal user token.
    """
    url = fastapi_app.url_path_for("update_user", user_id=999)
    response = await client.put(
        url,
        headers=normal_user_token_headers,
        json={"name": "Ghost User", "email": "ghost@example.com"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "User with id 999 not found"


@pytest.mark.anyio
async def test_delete_user(
    fastapi_app: FastAPI,
    client: AsyncClient,
    normal_user_token_headers,
) -> None:
    """Test deleting a user.

    Args:
        fastapi_app: current application fixture.
        client: client fixture.
        normal_user_token_headers: headers with normal user token.
    """
    # First create a user to delete
    create_url = fastapi_app.url_path_for("create_user")
    create_response = await client.post(
        create_url,
        headers=normal_user_token_headers,
        json={
            "name": "To Delete",
            "email": "to_delete@example.com",
            "password": "delete_password",
        },
    )
    user_id = create_response.json()["id"]

    # Now delete the user
    delete_url = fastapi_app.url_path_for("delete_user", user_id=user_id)
    delete_response = await client.delete(delete_url, headers=normal_user_token_headers)
    assert delete_response.status_code == status.HTTP_200_OK
    assert delete_response.json()["message"] == "User deleted successfully"

    # Verify the user is gone
    get_url = fastapi_app.url_path_for("get_user", user_id=user_id)
    get_response = await client.get(get_url, headers=normal_user_token_headers)
    assert get_response.status_code == status.HTTP_404_NOT_FOUND
