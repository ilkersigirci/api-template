from typing import List, Optional

from app.core.security import get_password_hash, verify_password
from app.models.user import User, UserCreate, UserInDB, UserUpdate
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User data access."""

    def __init__(self):
        self._users = [
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
        ]

    def get_by_id(self, id: int) -> Optional[User]:
        user = next((user for user in self._users if user.id == id), None)
        if user:
            return User(id=user.id, name=user.name, email=user.email)
        return None

    def get_by_email(self, email: str) -> Optional[UserInDB]:
        return next((user for user in self._users if user.email == email), None)

    def get_all(self) -> List[User]:
        return [
            User(id=user.id, name=user.name, email=user.email) for user in self._users
        ]

    def create(self, user_in: UserCreate) -> User:
        new_id = max(user.id for user in self._users) + 1 if self._users else 1
        user = UserInDB(
            id=new_id,
            name=user_in.name,
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
        )
        self._users.append(user)
        return User(id=user.id, name=user.name, email=user.email)

    def update(self, id: int, user_in: UserUpdate) -> Optional[User]:
        user = next((user for user in self._users if user.id == id), None)
        if user:
            update_data = user_in.model_dump(exclude_unset=True)

            # Hash password if it's included in update data
            if update_data.get("password"):
                hashed_password = get_password_hash(update_data.pop("password"))
                update_data["hashed_password"] = hashed_password

            updated_user = user.model_copy(update=update_data)
            self._users = [u if u.id != id else updated_user for u in self._users]
            return User(
                id=updated_user.id, name=updated_user.name, email=updated_user.email
            )
        return None

    def delete(self, id: int) -> bool:
        user = next((user for user in self._users if user.id == id), None)
        if user:
            self._users = [u for u in self._users if u.id != id]
            return True
        return False

    def authenticate(self, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return User(id=user.id, name=user.name, email=user.email)
