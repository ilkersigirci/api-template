from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.db.meta import meta


class BaseSQLAlchemyModel(DeclarativeBase):
    """Base for all sqlalchemy models."""

    metadata = meta

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
