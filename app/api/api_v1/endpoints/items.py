from typing import Annotated, List

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.dependencies.repositories import get_item_service
from app.models.item import Item, ItemCreate, ItemUpdate
from app.models.user import User
from app.services.item_service import ItemService

router = APIRouter()


@router.get("/", response_model=List[Item])
async def get_items(
    current_user: Annotated[User, Depends(get_current_user)],
    item_service: Annotated[ItemService, Depends(get_item_service)],
):
    return item_service.get_items()


@router.get("/{item_id}", response_model=Item)
async def get_item(
    item_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    item_service: Annotated[ItemService, Depends(get_item_service)],
):
    return item_service.get_item(item_id)


@router.post("/", response_model=Item)
async def create_item(
    item_in: ItemCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    item_service: Annotated[ItemService, Depends(get_item_service)],
):
    return item_service.create_item(item_in)


@router.put("/{item_id}", response_model=Item)
async def update_item(
    item_id: int,
    item_in: ItemUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    item_service: Annotated[ItemService, Depends(get_item_service)],
):
    return item_service.update_item(item_id, item_in)


@router.delete("/{item_id}")
async def delete_item(
    item_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    item_service: Annotated[ItemService, Depends(get_item_service)],
):
    item_service.delete_item(item_id)
    return {"message": "Item deleted successfully"}
