from typing import Annotated

from fastapi import Depends

from app.api.items.repository import ItemRepository
from app.api.items.service import ItemService


def get_item_repository() -> ItemRepository:
    return ItemRepository()


def get_item_service(
    item_repository: Annotated[ItemRepository, Depends(get_item_repository)],
) -> ItemService:
    return ItemService(item_repository)
