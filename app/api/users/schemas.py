import re
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

MIN_PASSWORD_LENGTH = 4


def validate_password_complexity(
    password: str, require_digit: bool = False, require_symbol: bool = False
) -> str:
    """Validates password complexity based on requirements.

    Args:
        password: The password string to validate.
        require_digit: Whether the password must contain a digit. Defaults to False.
        require_symbol: Whether the password must contain a symbol. Defaults to False.

    Returns:
        The password string if valid.

    Raises:
        ValueError: If the password does not meet complexity requirements.
    """
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(
            f"Password must be at least {MIN_PASSWORD_LENGTH} characters long"
        )
    if require_digit and not re.search(r"\d", password):
        raise ValueError("Password must contain at least one digit")
    if require_symbol and not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise ValueError("Password must contain at least one symbol")
    return password


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def password_complexity(cls, v: str) -> str:
        return validate_password_complexity(v)


class UserUpdate(UserBase):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_complexity(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return validate_password_complexity(v)
        return v


class UserInMemoryDB(UserBase):
    id: int
    hashed_password: str

    model_config = ConfigDict(from_attributes=True)


class User(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class UserInMemoryDBBase(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
