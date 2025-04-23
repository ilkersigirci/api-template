from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import String

from app.db.base import BaseSQLAlchemyModel


class UserModel(BaseSQLAlchemyModel):
    """User model"""

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(length=200))
    email: Mapped[str] = mapped_column(String(length=200), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(length=200))
