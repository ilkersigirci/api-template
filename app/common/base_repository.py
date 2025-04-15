from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Base repository interface for data access operations."""

    @abstractmethod
    async def get_by_id(self, id: int) -> T | None: ...

    @abstractmethod
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
        sort_by: str | None = None,
        order: str | None = "asc",
    ) -> list[T]: ...

    @abstractmethod
    async def create(self, obj_in) -> T: ...

    @abstractmethod
    async def update(self, id: int, obj_in) -> T | None: ...

    @abstractmethod
    async def delete(self, id: int) -> bool: ...
