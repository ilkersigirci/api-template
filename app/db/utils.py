import importlib
from pathlib import Path

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.settings import settings


async def create_database() -> None:
    """Create a database."""


async def drop_database() -> None:
    """Drop current database."""
    if Path(settings.DB_FILE).exists():
        Path(settings.DB_FILE).unlink()


def setup_db(app: FastAPI) -> None:  # pragma: no cover
    """Creates connection to the database.

    This function creates SQLAlchemy engine instance,
    session_factory for creating sessions
    and stores them in the application's state property.

    Args:
        FastAPI application instance.
    """
    engine = create_async_engine(
        settings.DB_URL,
        echo=settings.DB_ECHO,
        # connect_args={"check_same_thread": True},
    )
    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )
    app.state.db_engine = engine
    app.state.db_session_factory = session_factory


def load_all_db_models():
    """Import all SQLAlchemy models from models.py files within API directories.

    This function is needed for Alembic to properly detect models for migrations.
    It dynamically imports all the model classes from each models.py file found
    in the app/api subdirectories.
    """
    api_dir = Path(__file__).parent.parent / "api"

    for module_dir in api_dir.iterdir():
        if not module_dir.is_dir():
            continue

        models_file = module_dir / "models.py"
        if models_file.exists():
            module_name = f"app.api.{module_dir.name}.models"
            try:
                importlib.import_module(module_name)
            except ImportError as e:
                raise ValueError(f"Error importing {module_name}") from e
