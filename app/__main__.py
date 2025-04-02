import os
import shutil
from pathlib import Path

import uvicorn

from app.core.settings import settings


def set_multiproc_dir() -> None:
    """
    Sets mutiproc_dir env variable.

    This function cleans up the multiprocess directory
    and recreates it. This actions are required by prometheus-client
    to share metrics between processes.
    """
    shutil.rmtree(settings.PROMETHEUS_DIR, ignore_errors=True)
    Path(settings.PROMETHEUS_DIR).mkdir(parents=True)
    os.environ["PROMETHEUS_MULTIPROC_DIR"] = str(
        settings.PROMETHEUS_DIR.expanduser().absolute(),
    )


def main() -> None:
    """Entrypoint of the application."""
    set_multiproc_dir()

    uvicorn.run(
        "app.api.application:get_app",
        workers=settings.WORKERS,
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.value.lower(),
        factory=True,
    )


if __name__ == "__main__":
    main()
