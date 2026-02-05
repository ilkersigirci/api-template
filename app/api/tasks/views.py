"""Task router aggregation."""

from fastapi import APIRouter

router = APIRouter()

try:
    from app.api.tasks.workers import router as workers_router

    router.include_router(workers_router)
except RuntimeError:
    pass

try:
    from app.api.tasks.ml import router as ml_router

    router.include_router(ml_router)
except RuntimeError:
    pass
