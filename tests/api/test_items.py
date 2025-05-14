import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from starlette import status


@pytest.mark.anyio
async def test_get_items(
    fastapi_app: FastAPI,
    client_authenticated: AsyncClient,
) -> None:
    """Test getting all items.

    Args:
        fastapi_app: current application fixture.
        client_authenticated: client fixture with authentication.
    """
    url = fastapi_app.url_path_for("get_items")
    response = await client_authenticated.get(url)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2  # At least the two initial items should be present
    assert all("id" in item for item in data)
    assert all("name" in item for item in data)
    assert all("price" in item for item in data)


@pytest.mark.anyio
async def test_get_specific_item(
    fastapi_app: FastAPI,
    client_authenticated: AsyncClient,
) -> None:
    """Test getting a specific item by ID.

    Args:
        fastapi_app: current application fixture.
        client_authenticated: client fixture with authentication.
    """
    url = fastapi_app.url_path_for("get_item", item_id=1)
    response = await client_authenticated.get(url)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Item 1"
    assert data["description"] == "Description for Item 1"
    assert data["price"] == 10.5


@pytest.mark.anyio
async def test_get_nonexistent_item(
    fastapi_app: FastAPI,
    client_authenticated: AsyncClient,
) -> None:
    """Test getting an item that doesn't exist.

    Args:
        fastapi_app: current application fixture.
        client_authenticated: client fixture with authentication.
    """
    url = fastapi_app.url_path_for("get_item", item_id=999)
    response = await client_authenticated.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Item with id 999 not found"


@pytest.mark.anyio
async def test_create_item(
    fastapi_app: FastAPI,
    client_authenticated: AsyncClient,
) -> None:
    """Test creating a new item.

    Args:
        fastapi_app: current application fixture.
        client_authenticated: client fixture with authentication.
    """
    url = fastapi_app.url_path_for("create_item")
    response = await client_authenticated.post(
        url,
        json={"name": "New Item", "description": "A brand new item", "price": 25.99},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "New Item"
    assert data["description"] == "A brand new item"
    assert data["price"] == 25.99
    assert "id" in data


@pytest.mark.anyio
async def test_create_item_without_description(
    fastapi_app: FastAPI,
    client_authenticated: AsyncClient,
) -> None:
    """Test creating a new item without a description.

    Args:
        fastapi_app: current application fixture.
        client_authenticated: client fixture with authentication.
    """
    url = fastapi_app.url_path_for("create_item")
    response = await client_authenticated.post(
        url,
        json={"name": "No Description Item", "price": 15.99},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "No Description Item"
    assert data["description"] is None
    assert data["price"] == 15.99


@pytest.mark.anyio
async def test_create_item_missing_required_fields(
    fastapi_app: FastAPI,
    client_authenticated: AsyncClient,
) -> None:
    """Test creating a new item with missing required fields.

    Args:
        fastapi_app: current application fixture.
        client_authenticated: client fixture with authentication.
    """
    url = fastapi_app.url_path_for("create_item")
    # Missing name
    response = await client_authenticated.post(
        url,
        json={"price": 15.99},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()
    assert "detail" in data
    assert any("name" in error["loc"] for error in data["detail"])

    # Missing price
    response = await client_authenticated.post(
        url,
        json={"name": "Missing Price Item"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()
    assert "detail" in data
    assert any("price" in error["loc"] for error in data["detail"])


@pytest.mark.anyio
async def test_create_item_invalid_price(
    fastapi_app: FastAPI,
    client_authenticated: AsyncClient,
) -> None:
    """Test creating a new item with invalid price value.

    Args:
        fastapi_app: current application fixture.
        client_authenticated: client fixture with authentication.
    """
    url = fastapi_app.url_path_for("create_item")
    # Negative price - the API currently accepts negative prices
    response = await client_authenticated.post(
        url,
        json={"name": "Negative Price Item", "price": -10.0},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Negative Price Item"
    assert data["price"] == -10.0

    # Zero price - the API currently accepts zero prices
    response = await client_authenticated.post(
        url,
        json={"name": "Zero Price Item", "price": 0.0},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Zero Price Item"
    assert data["price"] == 0.0


@pytest.mark.anyio
async def test_update_item(
    fastapi_app: FastAPI,
    client_authenticated: AsyncClient,
) -> None:
    """Test updating an item.

    Args:
        fastapi_app: current application fixture.
        client_authenticated: client fixture with authentication.
    """
    url = fastapi_app.url_path_for("update_item", item_id=2)
    response = await client_authenticated.put(
        url,
        json={
            "name": "Updated Item 2",
            "description": "Updated description",
            "price": 22.0,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == 2
    assert data["name"] == "Updated Item 2"
    assert data["description"] == "Updated description"
    assert data["price"] == 22.0


@pytest.mark.anyio
async def test_update_nonexistent_item(
    fastapi_app: FastAPI,
    client_authenticated: AsyncClient,
) -> None:
    """Test updating an item that doesn't exist.

    Args:
        fastapi_app: current application fixture.
        client_authenticated: client fixture with authentication.
    """
    url = fastapi_app.url_path_for("update_item", item_id=999)
    response = await client_authenticated.put(
        url,
        json={
            "name": "Ghost Item",
            "description": "This item doesn't exist",
            "price": 0.0,
        },
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Item with id 999 not found"


@pytest.mark.anyio
async def test_delete_item(
    fastapi_app: FastAPI,
    client_authenticated: AsyncClient,
) -> None:
    """Test deleting an item.

    Args:
        fastapi_app: current application fixture.
        client_authenticated: client fixture with authentication.
    """
    # First create an item to delete
    create_url = fastapi_app.url_path_for("create_item")
    create_response = await client_authenticated.post(
        create_url,
        json={
            "name": "Item to Delete",
            "description": "This item will be deleted",
            "price": 9.99,
        },
    )
    item_id = create_response.json()["id"]

    # Now delete the item
    delete_url = fastapi_app.url_path_for("delete_item", item_id=item_id)
    delete_response = await client_authenticated.delete(delete_url)
    assert delete_response.status_code == status.HTTP_200_OK
    assert delete_response.json()["message"] == "Item deleted successfully"

    # Verify the item is gone
    get_url = fastapi_app.url_path_for("get_item", item_id=item_id)
    get_response = await client_authenticated.get(get_url)
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
async def test_delete_nonexistent_item(
    fastapi_app: FastAPI,
    client_authenticated: AsyncClient,
) -> None:
    """Test deleting an item that doesn't exist.

    Args:
        fastapi_app: current application fixture.
        client_authenticated: client fixture with authentication.
    """
    url = fastapi_app.url_path_for("delete_item", item_id=999)
    response = await client_authenticated.delete(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Item with id 999 not found"


@pytest.mark.anyio
async def test_access_items_unauthorized(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    """Test accessing items endpoints without authentication.

    Args:
        fastapi_app: current application fixture.
        client: client fixture without authentication.
    """
    # Try to get all items
    url = fastapi_app.url_path_for("get_items")
    response = await client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response.json()

    # Try to get a specific item
    url = fastapi_app.url_path_for("get_item", item_id=1)
    response = await client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response.json()

    # Try to create an item
    url = fastapi_app.url_path_for("create_item")
    response = await client.post(
        url,
        json={"name": "Unauthorized Item", "price": 25.99},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response.json()
