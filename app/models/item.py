from typing import Optional

from pydantic import BaseModel, ConfigDict


class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float


class ItemCreate(ItemBase):
    pass


class ItemUpdate(ItemBase):
    pass


class ItemInDB(ItemBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class Item(ItemInDB):
    pass
