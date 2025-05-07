from sqlalchemy import select

from app.api.auth.utils import get_password_hash
from app.api.users.models import UserModel
from app.api.users.schemas import UserCreate, UserInMemoryDB
from app.common.base_db_repository import BaseDBRepository
from app.common.in_memory_repository import InMemoryRepository

# NOTE: Data defined here instead of __init__. It is because, in each request
# init is called and it will reset the data.
user_inmemory_data = [
    UserInMemoryDB(
        id=1,
        name="John Doe",
        email="john@example.com",
        hashed_password=get_password_hash("password"),
    ),
    UserInMemoryDB(
        id=2,
        name="Jane Doe",
        email="jane@example.com",
        hashed_password=get_password_hash("password"),
    ),
    UserInMemoryDB(
        id=3,
        name="admin",
        email="admin@mail.com",
        hashed_password=get_password_hash("admin"),
    ),
]


class UserInMemoryRepository(InMemoryRepository[UserInMemoryDB]):
    """InMemory Repository for User data access."""

    def __init__(self):
        super().__init__(initial_data=user_inmemory_data)

    async def get_by_email(self, email: str) -> UserInMemoryDB | None:
        return next((user for user in self._data if user.email == email), None)


class UserRepository(BaseDBRepository[UserModel]):
    """SQLAlchemy Repository for User data access."""

    def __init__(self, session):
        super().__init__(model=UserModel, session=session)

    async def get_by_email(self, email: str) -> UserModel | None:
        result = await self.session.execute(
            select(self.model).where(self.model.email == email)
        )
        return result.scalar_one_or_none()

    async def create(self, obj_in: UserCreate) -> UserModel:
        """Create a new user with password hashing"""
        user_data = obj_in.model_dump(exclude={"password"})
        user_data["hashed_password"] = get_password_hash(obj_in.password)
        db_obj = self.model(**user_data)

        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj
