from typing import Any, Generic, TypeVar

from app.common.base_repository import BaseRepository

T = TypeVar("T")


class InMemoryRepository(BaseRepository[T], Generic[T]):
    def __init__(self, initial_data: list[T]):
        """Initialize the in-memory repository with initial data.

        NOTE:
            `initial_data` should be used as pass by reference. It is because, fastapi
            reinitialize the depencency on each request. So, if we pass by value,
            it will reset the data. Hence, CRUD operations will not work as expected.

            Actually, this is not a good practice to use in-memory repository as database.
            This is just for testing purpose. In production, we should use a proper database
            like PostgreSQL, MySQL, etc.
        """
        self._data = initial_data

    async def get_by_id(self, id: int) -> T | None:
        return next(
            (item for item in self._data if getattr(item, "id", None) == id), None
        )

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
        sort_by: str | None = None,
        order: str | None = "asc",
    ) -> list[T]:
        items = list(self._data)
        if filters:
            for field, value in filters.items():
                items = [item for item in items if getattr(item, field, None) == value]
        if sort_by and items and hasattr(items[0], sort_by):
            reverse = order.lower() == "desc"
            items.sort(key=lambda x: getattr(x, sort_by), reverse=reverse)
        return items[skip : skip + limit]

    async def create(self, obj_in) -> T:
        new_id = max((getattr(item, "id", 0) for item in self._data), default=0) + 1
        obj = (
            obj_in.model_copy(update={"id": new_id})
            if hasattr(obj_in, "model_copy")
            else obj_in
        )
        self._data.append(obj)
        return obj

    async def update(self, id: int, obj_in) -> T | None:
        item = await self.get_by_id(id)
        if item:
            update_data = (
                obj_in.model_dump(exclude_unset=True)
                if hasattr(obj_in, "model_dump")
                else {}
            )
            updated_item = (
                item.model_copy(update=update_data)
                if hasattr(item, "model_copy")
                else item
            )
            idx = next(
                (i for i, v in enumerate(self._data) if getattr(v, "id", None) == id),
                None,
            )
            if idx is not None:
                self._data.pop(idx)
                self._data.insert(idx, updated_item)
            return updated_item
        return None

    async def delete(self, id: int) -> bool:
        item = await self.get_by_id(id)
        if item:
            self._data.remove(item)
            return True
        return False
