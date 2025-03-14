import pytest
from fastapi.testclient import TestClient


def test_login(client: TestClient):
    """Test login endpoint."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "john@example.com", "password": "password"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_incorrect_password(client: TestClient):
    """Test login with incorrect password."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "john@example.com", "password": "wrong_password"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_register_user(client: TestClient):
    """Test user registration."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test User",
            "email": "test_user@example.com",
            "password": "test_password"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test_user@example.com"
    assert data["name"] == "Test User"
    assert "id" in data


def test_register_existing_user(client: TestClient):
    """Test registering with an email that's already in use."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "John Doe Clone",
            "email": "john@example.com",  # Already exists in repository
            "password": "test_password"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "A user with this email already exists"


def test_test_token(client: TestClient, normal_user_token_headers):
    """Test the token test endpoint."""
    response = client.post("/api/v1/auth/test-token", headers=normal_user_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["email"] == "john@example.com"
    assert data["name"] == "John Doe"
