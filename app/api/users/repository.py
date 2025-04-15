from typing import Optional

from app.api.auth.utils import get_password_hash
from app.api.users.schemas import UserInDB
from app.common.in_memory_repository import InMemoryRepository

# NOTE: Data defined here instead of __init__. It is because, in each request
# init is called and it will reset the data.
user_inmemory_data = [
    UserInDB(
        id=1,
        name="John Doe",
        email="john@example.com",
        hashed_password=get_password_hash("password"),
    ),
    UserInDB(
        id=2,
        name="Jane Doe",
        email="jane@example.com",
        hashed_password=get_password_hash("password"),
    ),
    UserInDB(
        id=3,
        name="ilker",
        email="ilker@example.com",
        hashed_password=get_password_hash("ilker"),
    ),
]


class UserRepository(InMemoryRepository[UserInDB]):
    """Repository for User data access."""

    def __init__(self):
        super().__init__(initial_data=user_inmemory_data)

    async def get_by_email(self, email: str) -> Optional[UserInDB]:
        return next((user for user in self._data if user.email == email), None)
