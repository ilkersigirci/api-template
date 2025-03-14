from typing import Optional

from pydantic import BaseModel


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

    class Config:
        orm_mode = True


class Item(ItemInDB):
    pass
