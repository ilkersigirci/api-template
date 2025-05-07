"""Exception classes for user-related operations."""

from fastapi import HTTPException, status


class UserError(HTTPException):
    """Base class for all user-related errors."""

    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        """Initialize with status code and detail message.

        Args:
            detail: Explanation of the error
            status_code: HTTP status code
        """
        super().__init__(status_code=status_code, detail=detail)


class UserNotFoundError(UserError):
    """Raised when a requested user does not exist."""

    def __init__(self, detail: str = "User not found"):
        """Initialize with 404 status and detail message.

        Args:
            detail: Explanation of why the user was not found
        """
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class UserAlreadyExistsError(UserError):
    """Raised when attempting to create a user with an email that already exists."""

    def __init__(self, detail: str = "User with this email already exists"):
        """Initialize with 409 status and detail message.

        Args:
            detail: Explanation of the conflict
        """
        super().__init__(detail=detail, status_code=status.HTTP_409_CONFLICT)


class AuthenticationError(UserError):
    """Raised when authentication fails due to invalid credentials."""

    def __init__(self, detail: str = "Invalid authentication credentials"):
        """Initialize with 401 status and detail message.

        Args:
            detail: Explanation of the authentication failure
        """
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)


class PermissionDeniedError(UserError):
    """Raised when a user doesn't have permission to perform an action."""

    def __init__(self, detail: str = "Permission denied"):
        """Initialize with 403 status and detail message.

        Args:
            detail: Explanation of why permission was denied
        """
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)
