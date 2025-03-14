import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.security import create_access_token
from app.models.user import User


@pytest.fixture
def client():
    """Create a test client for the app."""
    return TestClient(app)


@pytest.fixture
def normal_user_token():
    """Create a token for a normal user."""
    return create_access_token(subject="1")


@pytest.fixture
def normal_user_token_headers(normal_user_token):
    """Return authorization headers for normal user."""
    return {"Authorization": f"Bearer {normal_user_token}"}


@pytest.fixture
def test_user():
    """Return a sample test user."""
    return User(id=1, name="John Doe", email="john@example.com")
