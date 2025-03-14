from typing import List

from fastapi import HTTPException

from app.models.item import Item, ItemCreate, ItemUpdate
from app.repositories.item_repository import ItemRepository


class ItemService:
    def __init__(self, item_repository: ItemRepository):
        self.item_repository = item_repository

    def get_item(self, item_id: int) -> Item:
        item = self.item_repository.get_by_id(item_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Item not found")
        return item

    def get_items(self) -> List[Item]:
        return self.item_repository.get_all()

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
