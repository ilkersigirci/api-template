from fastapi import APIRouter, Depends

from app.api.auth.deps import get_current_user
from app.api.auth.views import router as auth
from app.api.echo.views import router as echo
from app.api.items.views import router as items
from app.api.redis.views import router as redis
from app.api.tasks.views import router as tasks
from app.api.users.views import router as users

api_router = APIRouter()

api_router.include_router(auth)

api_router.include_router(echo, dependencies=[Depends(get_current_user)])

api_router.include_router(users, dependencies=[Depends(get_current_user)])

api_router.include_router(items, dependencies=[Depends(get_current_user)])

api_router.include_router(redis, dependencies=[Depends(get_current_user)])

api_router.include_router(tasks)
