from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.auth.deps import get_current_user
from app.api.auth.schemas import Token
from app.api.users.deps import get_user_service
from app.api.users.schemas import User, UserCreate
from app.api.users.service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    auth_result = await user_service.authenticate(
        email=form_data.username, password=form_data.password
    )
    return Token(access_token=auth_result["access_token"], token_type="bearer")


@router.post("/register", response_model=User)
async def register_user(
    user_in: UserCreate, user_service: Annotated[UserService, Depends(get_user_service)]
):
    """
    Register a new user
    """
    return await user_service.create_user(user_in)


@router.post("/test-token", response_model=User)
async def test_token(current_user: Annotated[User, Depends(get_current_user)]):
    """
    Test access token
    """
    return current_user
