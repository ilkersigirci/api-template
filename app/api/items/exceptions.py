"""Exception classes for item-related operations."""

from app.common.base_exceptions import (
    APIError,
    ResourceAlreadyExistsError,
    ResourceNotFoundError,
)


class ItemError(APIError):
    """Base class for all item-related errors."""


class ItemNotFoundError(ResourceNotFoundError):
    """Raised when a requested item does not exist."""

    def __init__(self, detail: str = "Item not found"):
        """Initialize with 404 status and detail message.

        Args:
            detail: Explanation of why the item was not found
        """
        super().__init__(detail=detail)


class ItemOperationError(ItemError):
    """Raised when an operation on an item fails."""

    def __init__(self, detail: str = "Item operation failed"):
        """Initialize with 500 status and detail message.

        Args:
            detail: Explanation of the operation failure
        """
        super().__init__(detail=detail, status_code=500)


class ItemAlreadyExistsError(ResourceAlreadyExistsError):
    """Raised when attempting to create an item that already exists."""

    def __init__(self, detail: str = "Item already exists"):
        """Initialize with 409 status and detail message.

        Args:
            detail: Explanation of the conflict
        """
        super().__init__(detail=detail)
