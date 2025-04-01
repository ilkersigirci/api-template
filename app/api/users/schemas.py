from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDB(UserBase):
    id: int
    hashed_password: str

    model_config = ConfigDict(from_attributes=True)


class User(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class UserInDBBase(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
