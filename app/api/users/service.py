from datetime import timedelta
from typing import List

from fastapi import HTTPException

from app.api.auth.utils import create_access_token
from app.api.users.repository import UserRepository
from app.api.users.schemas import User, UserCreate, UserUpdate
from app.core.settings import settings


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get_user(self, user_id: int) -> User:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def get_users(self) -> List[User]:
        return await self.user_repository.get_all()

    async def create_user(self, user_in: UserCreate) -> User:
        # Check if a user with this email already exists
        user = await self.user_repository.get_by_email(user_in.email)
        if user:
            raise HTTPException(
                status_code=400, detail="A user with this email already exists"
            )
        return await self.user_repository.create(user_in)

    async def update_user(self, user_id: int, user_in: UserUpdate) -> User:
        updated_user = await self.user_repository.update(user_id, user_in)
        if updated_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return updated_user

    async def delete_user(self, user_id: int) -> bool:
        success = await self.user_repository.delete(user_id)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        return success

    async def authenticate(self, email: str, password: str) -> dict:
        user = await self.user_repository.authenticate(email, password)
        if not user:
            raise HTTPException(status_code=401, detail="Incorrect email or password")

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=str(user.id), expires_delta=access_token_expires
        )

        return {"access_token": access_token, "token_type": "bearer", "user": user}

    async def get_by_email(self, email: str) -> User:
        user = await self.user_repository.get_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return User(id=user.id, name=user.name, email=user.email)
