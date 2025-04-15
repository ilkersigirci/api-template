from typing import Annotated

from fastapi import Depends

from app.api.users.repository import UserRepository
from app.api.users.service import UserService


def get_user_repository() -> UserRepository:
    return UserRepository()


def get_user_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserService:
    return UserService(user_repository)
