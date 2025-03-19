from fastapi import APIRouter, Depends

from app.api.v1.endpoints import auth, echo, items, redis, users
from app.dependencies.auth import get_current_user

api_router = APIRouter()

api_router.include_router(
    echo.router,
    prefix="/echo",
    tags=["echo"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"],
)
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(
    items.router,
    prefix="/items",
    tags=["items"],
    dependencies=[Depends(get_current_user)],
)

api_router.include_router(
    redis.router,
    prefix="/redis",
    tags=["redis"],
    dependencies=[Depends(get_current_user)],
)
