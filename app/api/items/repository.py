from app.api.items.models import ItemModel
from app.api.items.schemas import Item
from app.common.base_db_repository import BaseDBRepository
from app.common.in_memory_repository import InMemoryRepository

# NOTE: Data defined here instead of __init__. It is because, in each request
# init is called and it will reset the data.
item_inmemory_data = [
    Item(id=1, name="Item 1", description="Description for Item 1", price=10.5),
    Item(id=2, name="Item 2", price=20.0),
]


class ItemInMemoryRepository(InMemoryRepository[Item]):
    """Repository for Item data access."""

    def __init__(self):
        super().__init__(initial_data=item_inmemory_data)


class ItemRepository(BaseDBRepository[ItemModel]):
    """SQLAlchemy Repository for Item data access."""

    def __init__(self, session):
        super().__init__(model=ItemModel, session=session)
