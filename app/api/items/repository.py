from app.api.items.schemas import Item
from app.common.in_memory_repository import InMemoryRepository


class ItemRepository(InMemoryRepository[Item]):
    """Repository for Item data access."""

    def __init__(self):
        initial_data = [
            Item(id=1, name="Item 1", description="Description for Item 1", price=10.5),
            Item(id=2, name="Item 2", price=20.0),
        ]
        super().__init__(initial_data=initial_data)
