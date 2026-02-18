"""Task router aggregation."""

from fastapi import APIRouter

from app.api.tasks.general import router as workers_router
from app.api.tasks.ml import router as ml_router

router = APIRouter()
router.include_router(workers_router)
router.include_router(ml_router)
