from typing import Any, Dict, List, Optional

from fastapi import HTTPException

from app.api.items.repository import ItemRepository
from app.api.items.schemas import Item, ItemCreate, ItemUpdate


class ItemService:
    def __init__(self, item_repository: ItemRepository):
        self.item_repository = item_repository

    def get_items(  # noqa: PLR0913
        self,
        skip: int = 0,
        limit: int = 100,
        name: Optional[str] = None,
        description: Optional[str] = None,
        sort_by: Optional[str] = None,
        order: Optional[str] = "asc",
    ) -> List[Item]:
        filters: Dict[str, Any] = {}
        if name:
            filters["name"] = name
        if description:
            filters["description"] = description

        return self.item_repository.get_items(
            skip=skip, limit=limit, filters=filters, sort_by=sort_by, order=order
        )

    def get_item(self, item_id: int) -> Item:
        item = self.item_repository.get_by_id(item_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Item not found")
        return item

    def create_item(self, item_in: ItemCreate) -> Item:
        return self.item_repository.create(item_in)

    def update_item(self, item_id: int, item_in: ItemUpdate) -> Item:
        updated_item = self.item_repository.update(item_id, item_in)
        if updated_item is None:
            raise HTTPException(status_code=404, detail="Item not found")
        return updated_item

    def delete_item(self, item_id: int) -> bool:
        success = self.item_repository.delete(item_id)
        if not success:
            raise HTTPException(status_code=404, detail="Item not found")
        return success
