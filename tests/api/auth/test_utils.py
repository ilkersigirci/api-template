from datetime import timedelta

import pytest
from app.api.auth.utils import (
    create_access_token,
    get_password_hash,
    verify_password,
)


def test_password_hashing():
    """Test password hashing and verification."""
    password = "secret_password"
    hashed_password = get_password_hash(password)

    # The hashed password should be different from the original
    assert hashed_password != password

    # Verify the password works with the hash
    assert verify_password(password, hashed_password) is True

    # Verify an incorrect password fails
    assert verify_password("wrong_password", hashed_password) is False


@pytest.mark.parametrize("expires_delta", [None, timedelta(minutes=5)])
def test_create_access_token(expires_delta):
    """Test token creation with and without a custom expiry time."""
    token = create_access_token(subject="test_user_id", expires_delta=expires_delta)
    assert isinstance(token, str)
    assert len(token) > 0
