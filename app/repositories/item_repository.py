from typing import List, Optional

from app.models.item import Item, ItemCreate, ItemUpdate
from app.repositories.base import BaseRepository


class ItemRepository(BaseRepository[Item]):
    """Repository for Item data access."""

    def __init__(self):
        self._items = [
            Item(id=1, name="Item 1", description="Description for Item 1", price=10.5),
            Item(id=2, name="Item 2", price=20.0),
        ]

    def get_by_id(self, id: int) -> Optional[Item]:
        return next((item for item in self._items if item.id == id), None)

    def get_all(self) -> List[Item]:
        return self._items

    def create(self, item_in: ItemCreate) -> Item:
        new_id = max(item.id for item in self._items) + 1 if self._items else 1
        item = Item(
            id=new_id,
            name=item_in.name,
            description=item_in.description,
            price=item_in.price,
        )
        self._items.append(item)
        return item

    def update(self, id: int, item_in: ItemUpdate) -> Optional[Item]:
        item = self.get_by_id(id)
        if item:
            update_data = item_in.model_dump(exclude_unset=True)
            updated_item = item.model_copy(update=update_data)
            self._items = [i if i.id != id else updated_item for i in self._items]
            return updated_item
        return None

    def delete(self, id: int) -> bool:
        item = self.get_by_id(id)
        if item:
            self._items = [i for i in self._items if i.id != id]
            return True
        return False
