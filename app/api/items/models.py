from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import String

from app.db.base import BaseSQLAlchemyModel


class ItemModel(BaseSQLAlchemyModel):
    """User model"""

    __tablename__ = "item"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(length=200))
    description: Mapped[str | None] = mapped_column(String(length=200), nullable=True)
    price: Mapped[float] = mapped_column(String(length=200))
