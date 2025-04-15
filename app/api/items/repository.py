from typing import Any, Optional

from app.api.items.schemas import Item, ItemCreate, ItemUpdate
from app.common.base_repository import BaseRepository


class ItemRepository(BaseRepository[Item]):
    """Repository for Item data access."""

    def __init__(self):
        self._items = [
            Item(id=1, name="Item 1", description="Description for Item 1", price=10.5),
            Item(id=2, name="Item 2", price=20.0),
        ]

    async def get_by_id(self, id: int) -> Optional[Item]:
        return next((item for item in self._items if item.id == id), None)

    async def get_all(self) -> list[Item]:
        return self._items

    async def create(self, item_in: ItemCreate) -> Item:
        new_id = max(item.id for item in self._items) + 1 if self._items else 1
        item = Item(
            id=new_id,
            name=item_in.name,
            description=item_in.description,
            price=item_in.price,
        )
        self._items.append(item)
        return item

    async def update(self, id: int, item_in: ItemUpdate) -> Optional[Item]:
        item = await self.get_by_id(id)
        if item:
            update_data = item_in.model_dump(exclude_unset=True)
            updated_item = item.model_copy(update=update_data)
            self._items = [i if i.id != id else updated_item for i in self._items]
            return updated_item
        return None

    async def delete(self, id: int) -> bool:
        item = await self.get_by_id(id)
        if item:
            self._items = [i for i in self._items if i.id != id]
            return True
        return False

    async def get_items(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
        sort_by: Optional[str] = None,
        order: Optional[str] = "asc",
    ) -> list[Item]:
        items = list(self._items)

        # Apply filters if provided
        if filters:
            for field, value in filters.items():
                items = [item for item in items if getattr(item, field, None) == value]

        # Apply sorting if requested
        if sort_by and hasattr(Item, sort_by):
            reverse = order.lower() == "desc"
            items.sort(key=lambda x: getattr(x, sort_by), reverse=reverse)

        # Apply pagination
        return items[skip : skip + limit]
