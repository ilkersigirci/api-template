from datetime import timedelta

from app.core.security import create_access_token, get_password_hash, verify_password


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


def test_create_access_token():
    """Test token creation."""
    subject = "test_user_id"
    token = create_access_token(subject=subject)

    # Simply check that we get a non-empty string
    assert isinstance(token, str)
    assert len(token) > 0


def test_create_access_token_with_expiry():
    """Test token creation with custom expiry time."""
    subject = "test_user_id"
    expires_delta = timedelta(minutes=5)
    token = create_access_token(subject=subject, expires_delta=expires_delta)

    # Simply check that we get a non-empty string
    assert isinstance(token, str)
    assert len(token) > 0
