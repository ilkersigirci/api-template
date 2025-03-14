import pytest
from fastapi.testclient import TestClient


def test_get_items(client: TestClient, normal_user_token_headers):
    """Test getting all items."""
    response = client.get("/api/v1/items/", headers=normal_user_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2  # At least the two initial items should be present
    assert all("id" in item for item in data)
    assert all("name" in item for item in data)
    assert all("price" in item for item in data)


def test_get_specific_item(client: TestClient, normal_user_token_headers):
    """Test getting a specific item by ID."""
    response = client.get("/api/v1/items/1", headers=normal_user_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Item 1"
    assert data["description"] == "Description for Item 1"
    assert data["price"] == 10.5


def test_get_nonexistent_item(client: TestClient, normal_user_token_headers):
    """Test getting an item that doesn't exist."""
    response = client.get("/api/v1/items/999", headers=normal_user_token_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


def test_create_item(client: TestClient, normal_user_token_headers):
    """Test creating a new item."""
    response = client.post(
        "/api/v1/items/",
        headers=normal_user_token_headers,
        json={
            "name": "New Item",
            "description": "A brand new item",
            "price": 25.99
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Item"
    assert data["description"] == "A brand new item"
    assert data["price"] == 25.99
    assert "id" in data


def test_create_item_without_description(client: TestClient, normal_user_token_headers):
    """Test creating a new item without a description."""
    response = client.post(
        "/api/v1/items/",
        headers=normal_user_token_headers,
        json={
            "name": "No Description Item",
            "price": 15.99
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "No Description Item"
    assert data["description"] is None
    assert data["price"] == 15.99


def test_update_item(client: TestClient, normal_user_token_headers):
    """Test updating an item."""
    response = client.put(
        "/api/v1/items/2",
        headers=normal_user_token_headers,
        json={
            "name": "Updated Item 2",
            "description": "Updated description",
            "price": 22.0
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 2
    assert data["name"] == "Updated Item 2"
    assert data["description"] == "Updated description"
    assert data["price"] == 22.0


def test_update_nonexistent_item(client: TestClient, normal_user_token_headers):
    """Test updating an item that doesn't exist."""
    response = client.put(
        "/api/v1/items/999",
        headers=normal_user_token_headers,
        json={
            "name": "Ghost Item",
            "description": "This item doesn't exist",
            "price": 0.0
        }
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


def test_delete_item(client: TestClient, normal_user_token_headers):
    """Test deleting an item."""
    # First create an item to delete
    create_response = client.post(
        "/api/v1/items/",
        headers=normal_user_token_headers,
        json={
            "name": "Item to Delete",
            "description": "This item will be deleted",
            "price": 9.99
        }
    )
    item_id = create_response.json()["id"]

    # Now delete the item
    delete_response = client.delete(
        f"/api/v1/items/{item_id}",
        headers=normal_user_token_headers
    )
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Item deleted successfully"

    # Verify the item is gone
    get_response = client.get(
        f"/api/v1/items/{item_id}",
        headers=normal_user_token_headers
    )
    assert get_response.status_code == 404
