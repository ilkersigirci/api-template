from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.dependencies.repositories import get_item_service
from app.models.item import Item, ItemCreate, ItemUpdate
from app.services.item_service import ItemService

router = APIRouter()


@router.get("/")
async def get_items(  # noqa: PLR0913
    item_service: Annotated[ItemService, Depends(get_item_service)],
    skip: Annotated[int, Query(ge=0, description="Number of items to skip")] = 0,
    limit: Annotated[
        int, Query(ge=1, le=100, description="Number of items to return")
    ] = 100,
    name: Annotated[str | None, Query(description="Filter items by name")] = None,
    description: Annotated[
        str | None, Query(description="Filter items by description")
    ] = None,
    sort_by: Annotated[str | None, Query(description="Field to sort by")] = None,
    order: Annotated[str | None, Query(description="Sort order (asc or desc)")] = "asc",
) -> list[Item]:
    return item_service.get_items(
        skip=skip,
        limit=limit,
        name=name,
        description=description,
        sort_by=sort_by,
        order=order,
    )


@router.get("/{item_id}")
async def get_item(
    item_id: int,
    item_service: Annotated[ItemService, Depends(get_item_service)],
) -> Item:
    return item_service.get_item(item_id)


@router.post("/")
async def create_item(
    item_in: ItemCreate,
    item_service: Annotated[ItemService, Depends(get_item_service)],
) -> Item:
    return item_service.create_item(item_in)


@router.put("/{item_id}")
async def update_item(
    item_id: int,
    item_in: ItemUpdate,
    item_service: Annotated[ItemService, Depends(get_item_service)],
) -> Item:
    return item_service.update_item(item_id, item_in)


@router.delete("/{item_id}")
async def delete_item(
    item_id: int,
    item_service: Annotated[ItemService, Depends(get_item_service)],
) -> dict:
    item_service.delete_item(item_id)
    return {"message": "Item deleted successfully"}
