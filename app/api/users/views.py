from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.auth.deps import get_current_user
from app.api.users.schemas import User, UserCreate, UserUpdate
from app.api.users.service import UserService
from app.dependencies.repositories import get_user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/")
async def get_users(
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> list[User]:
    return user_service.get_users()


@router.get("/me")
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    return current_user


@router.get("/{user_id}")
async def get_user(
    user_id: int,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> User:
    return user_service.get_user(user_id)


@router.post("/")
async def create_user(
    user_in: UserCreate,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> User:
    return user_service.create_user(user_in)


@router.put("/{user_id}")
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> User:
    return user_service.update_user(user_id, user_in)


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> dict:
    user_service.delete_user(user_id)
    return {"message": "User deleted successfully"}
