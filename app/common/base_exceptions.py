"""Base exception classes for API operations."""

from fastapi import HTTPException, status


class APIError(HTTPException):
    """Base class for all API-related errors."""

    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        """Initialize with status code and detail message.

        Args:
            detail: Explanation of the error
            status_code: HTTP status code
        """
        super().__init__(status_code=status_code, detail=detail)


class ResourceNotFoundError(APIError):
    """Raised when a requested resource does not exist."""

    def __init__(self, detail: str = "Resource not found"):
        """Initialize with 404 status and detail message.

        Args:
            detail: Explanation of why the resource was not found
        """
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class ResourceAlreadyExistsError(APIError):
    """Raised when attempting to create a resource that already exists."""

    def __init__(self, detail: str = "Resource already exists"):
        """Initialize with 409 status and detail message.

        Args:
            detail: Explanation of the conflict
        """
        super().__init__(detail=detail, status_code=status.HTTP_409_CONFLICT)


class AuthenticationError(APIError):
    """Raised when authentication fails due to invalid credentials."""

    def __init__(self, detail: str = "Invalid authentication credentials"):
        """Initialize with 401 status and detail message.

        Args:
            detail: Explanation of the authentication failure
        """
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)


class PermissionDeniedError(APIError):
    """Raised when a user doesn't have permission to perform an action."""

    def __init__(self, detail: str = "Permission denied"):
        """Initialize with 403 status and detail message.

        Args:
            detail: Explanation of why permission was denied
        """
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)
