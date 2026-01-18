import pytest
from app.utils.general import is_module_installed


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
    with pytest.raises(
        ImportError, match=r"Module nonexistent_module_xyz123 is not installed\."
    ):
        is_module_installed("nonexistent_module_xyz123", throw_error=True)
