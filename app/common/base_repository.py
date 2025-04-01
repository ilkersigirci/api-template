from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Base repository interface for data access operations."""

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        pass

    @abstractmethod
    def get_all(self) -> List[T]:
        pass

    @abstractmethod
    def create(self, obj_in) -> T:
        pass

    @abstractmethod
    def update(self, id: int, obj_in) -> Optional[T]:
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        pass
