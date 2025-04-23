from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.items.repository import ItemRepository
from app.api.items.service import ItemService
from app.db.deps import get_db_session


def get_item_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ItemRepository:
    return ItemRepository(session=session)


def get_item_service(
    item_repository: Annotated[ItemRepository, Depends(get_item_repository)],
) -> ItemService:
    return ItemService(item_repository)
