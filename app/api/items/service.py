from typing import Any, Dict, List, Optional

from app.api.items.exceptions import ItemNotFoundError
from app.api.items.repository import ItemRepository
from app.api.items.schemas import Item, ItemCreate, ItemUpdate


class ItemService:
    """Service layer for item-related operations."""

    def __init__(self, item_repository: ItemRepository):
        """Initializes the ItemService.

        Args:
            item_repository: The repository for item data access.
        """
        self.item_repository = item_repository

    async def get_items(  # noqa: PLR0913
        self,
        skip: int = 0,
        limit: int = 100,
        name: Optional[str] = None,
        description: Optional[str] = None,
        sort_by: Optional[str] = None,
        order: Optional[str] = "asc",
    ) -> List[Item]:
        """Retrieves a list of items with optional filtering and sorting.

        Args:
            skip: Number of items to skip (pagination).
            limit: Maximum number of items to return (pagination).
            name: Optional filter by item name.
            description: Optional filter by item description.
            sort_by: Optional field to sort results by.
            order: Sort order, either "asc" or "desc".

        Returns:
            A list of item objects matching the criteria.
        """
        filters: Dict[str, Any] = {}
        if name:
            filters["name"] = name
        if description:
            filters["description"] = description

        return await self.item_repository.get_all(
            skip=skip, limit=limit, filters=filters, sort_by=sort_by, order=order
        )

    async def get_item(self, item_id: int) -> Item:
        """Retrieves an item by its ID.

        Args:
            item_id: The ID of the item to retrieve.

        Returns:
            The item object.

        Raises:
            ItemNotFoundError: If the item with the given ID is not found.
        """
        item = await self.item_repository.get_by_id(item_id)
        if item is None:
            raise ItemNotFoundError(f"Item with id {item_id} not found")
        return item

    async def create_item(self, item_in: ItemCreate) -> Item:
        """Creates a new item.

        Args:
            item_in: The data for the new item.

        Returns:
            The newly created item object.
        """
        return await self.item_repository.create(item_in)

    async def update_item(self, item_id: int, item_in: ItemUpdate) -> Item:
        """Updates an existing item.

        Args:
            item_id: The ID of the item to update.
            item_in: The data to update the item with.

        Returns:
            The updated item object.

        Raises:
            ItemNotFoundError: If the item with the given ID is not found.
        """
        updated_item = await self.item_repository.update(item_id, item_in)
        if updated_item is None:
            raise ItemNotFoundError(f"Item with id {item_id} not found")
        return updated_item

    async def delete_item(self, item_id: int) -> bool:
        """Deletes an item.

        Args:
            item_id: The ID of the item to delete.

        Returns:
            True if the deletion was successful.

        Raises:
            ItemNotFoundError: If the item with the given ID is not found.
            ItemOperationError: If the deletion fails unexpectedly after the item was found.
        """
        success = await self.item_repository.delete(item_id)
        if not success:
            raise ItemNotFoundError(f"Item with id {item_id} not found")
        return success
