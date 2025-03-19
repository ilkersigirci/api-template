from fastapi import APIRouter, Depends

from app.api.v2.endpoints import echo
from app.dependencies.auth import get_current_user

api_router = APIRouter()

api_router.include_router(
    echo.router,
    prefix="/echo",
    tags=["echo"],
    dependencies=[Depends(get_current_user)],
)
