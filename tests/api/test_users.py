import pytest
from fastapi.testclient import TestClient


def test_get_users(client: TestClient, normal_user_token_headers):
    """Test getting all users."""
    response = client.get("/api/v1/users/", headers=normal_user_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2  # At least the two initial users should be present
    assert all("id" in user for user in data)
    assert all("email" in user for user in data)
    assert all("name" in user for user in data)


def test_get_current_user(client: TestClient, normal_user_token_headers):
    """Test getting the current user."""
    response = client.get("/api/v1/users/me", headers=normal_user_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["email"] == "john@example.com"
    assert data["name"] == "John Doe"


def test_get_specific_user(client: TestClient, normal_user_token_headers):
    """Test getting a specific user by ID."""
    response = client.get("/api/v1/users/2", headers=normal_user_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 2
    assert data["email"] == "jane@example.com"
    assert data["name"] == "Jane Doe"


def test_get_nonexistent_user(client: TestClient, normal_user_token_headers):
    """Test getting a user that doesn't exist."""
    response = client.get("/api/v1/users/999", headers=normal_user_token_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_create_user(client: TestClient, normal_user_token_headers):
    """Test creating a new user."""
    response = client.post(
        "/api/v1/users/",
        headers=normal_user_token_headers,
        json={
            "name": "Created User",
            "email": "created@example.com",
            "password": "created_password"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Created User"
    assert data["email"] == "created@example.com"
    assert "id" in data


def test_update_user(client: TestClient, normal_user_token_headers):
    """Test updating a user."""
    response = client.put(
        "/api/v1/users/2",
        headers=normal_user_token_headers,
        json={
            "name": "Updated Jane",
            "email": "updated_jane@example.com"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 2
    assert data["name"] == "Updated Jane"
    assert data["email"] == "updated_jane@example.com"


def test_update_nonexistent_user(client: TestClient, normal_user_token_headers):
    """Test updating a user that doesn't exist."""
    response = client.put(
        "/api/v1/users/999",
        headers=normal_user_token_headers,
        json={
            "name": "Ghost User",
            "email": "ghost@example.com"
        }
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_delete_user(client: TestClient, normal_user_token_headers):
    """Test deleting a user."""
    # First create a user to delete
    create_response = client.post(
        "/api/v1/users/",
        headers=normal_user_token_headers,
        json={
            "name": "To Delete",
            "email": "to_delete@example.com",
            "password": "delete_password"
        }
    )
    user_id = create_response.json()["id"]

    # Now delete the user
    delete_response = client.delete(
        f"/api/v1/users/{user_id}",
        headers=normal_user_token_headers
    )
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "User deleted successfully"

    # Verify the user is gone
    get_response = client.get(
        f"/api/v1/users/{user_id}",
        headers=normal_user_token_headers
    )
    assert get_response.status_code == 404
