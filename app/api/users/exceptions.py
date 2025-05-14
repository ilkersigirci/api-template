"""Exception classes for user-related operations."""

from app.common.base_exceptions import (
    APIError,
    AuthenticationError,  # noqa: F401
    PermissionDeniedError,  # noqa: F401
    ResourceAlreadyExistsError,
    ResourceNotFoundError,
)


class UserError(APIError):
    """Base class for all user-related errors."""


class UserNotFoundError(ResourceNotFoundError):
    """Raised when a requested user does not exist."""

    def __init__(self, detail: str = "User not found"):
        """Initialize with 404 status and detail message.

        Args:
            detail: Explanation of why the user was not found
        """
        super().__init__(detail=detail)


class UserAlreadyExistsError(ResourceAlreadyExistsError):
    """Raised when attempting to create a user with an email that already exists."""

    def __init__(self, detail: str = "User with this email already exists"):
        """Initialize with 409 status and detail message.

        Args:
            detail: Explanation of the conflict
        """
        super().__init__(detail=detail)
