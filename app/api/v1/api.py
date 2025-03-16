from fastapi import APIRouter, Depends

from app.api.v1.endpoints import auth, items, users
from app.dependencies.auth import get_current_user

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(
    items.router,
    prefix="/items",
    tags=["items"],
    dependencies=[Depends(get_current_user)],
)
