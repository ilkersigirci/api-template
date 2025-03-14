from typing import Annotated

from fastapi import Depends

from app.repositories.item_repository import ItemRepository
from app.repositories.user_repository import UserRepository
from app.services.item_service import ItemService
from app.services.user_service import UserService


# Repository dependencies
def get_user_repository() -> UserRepository:
    return UserRepository()


def get_item_repository() -> ItemRepository:
    return ItemRepository()


# Service dependencies
def get_user_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserService:
    return UserService(user_repository)


def get_item_service(
    item_repository: Annotated[ItemRepository, Depends(get_item_repository)],
) -> ItemService:
    return ItemService(item_repository)
