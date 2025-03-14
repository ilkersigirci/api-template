import os
import pytest

from app.utils.general import check_env_vars, is_module_installed


def test_check_env_vars_with_empty_list():
    """Test check_env_vars with an empty list."""
    # Should not raise any exception
    check_env_vars([])
    check_env_vars(None)


def test_check_env_vars_with_existing_var():
    """Test check_env_vars with vars that exist."""
    # Set a test environment variable
    os.environ["TEST_ENV_VAR"] = "test_value"

    # Should not raise any exception
    check_env_vars(["TEST_ENV_VAR"])

    # Clean up
    del os.environ["TEST_ENV_VAR"]


def test_check_env_vars_with_missing_var():
    """Test check_env_vars with missing vars."""
    # Make sure the variable doesn't exist
    if "NONEXISTENT_VAR" in os.environ:
        del os.environ["NONEXISTENT_VAR"]

    # Should raise ValueError
    with pytest.raises(ValueError, match="Please set NONEXISTENT_VAR env var."):
        check_env_vars(["NONEXISTENT_VAR"])


def test_is_module_installed_existing():
    """Test is_module_installed with a module that exists."""
    # os is always available in Python
    assert is_module_installed("os") is True

    # With throw_error=True should still return True
    assert is_module_installed("os", throw_error=True) is True


def test_is_module_installed_nonexisting():
    """Test is_module_installed with a module that doesn't exist."""
    # Use a module name that's unlikely to exist
    assert is_module_installed("nonexistent_module_xyz123") is False

    # With throw_error=True should raise ImportError
    with pytest.raises(ImportError, match="Module nonexistent_module_xyz123 is not installed."):
        is_module_installed("nonexistent_module_xyz123", throw_error=True)
