from datetime import timedelta
from typing import List

from app.api.auth.utils import create_access_token, get_password_hash, verify_password
from app.api.users.exceptions import (
    AuthenticationError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.api.users.repository import UserRepository
from app.api.users.schemas import User, UserCreate, UserUpdate
from app.core.settings import settings


class UserService:
    """Service layer for user-related operations."""

    def __init__(self, user_repository: UserRepository):
        """Initializes the UserService.

        Args:
            user_repository: The repository for user data access.
        """
        self.user_repository = user_repository

    async def get_user(self, user_id: int) -> User:
        """Retrieves a user by their ID.

        Args:
            user_id: The ID of the user to retrieve.

        Returns:
            The user object.

        Raises:
            UserNotFoundError: If the user with the given ID is not found.
        """
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User with id {user_id} not found")
        return user

    async def get_users(self) -> List[User]:
        """Retrieves all users.

        Returns:
            A list of all user objects.
        """
        return await self.user_repository.get_all()

    async def create_user(self, user_in: UserCreate) -> User:
        """Creates a new user.

        Args:
            user_in: The data for the new user. Pydantic model validation handles password complexity.

        Returns:
            The newly created user object.

        Raises:
            UserAlreadyExistsError: If a user with the same email already exists.
        """
        existing_user = await self.user_repository.get_by_email(user_in.email)
        if existing_user:
            raise UserAlreadyExistsError(
                f"A user with email {user_in.email} already exists"
            )

        return await self.user_repository.create(user_in)

    async def update_user(self, user_id: int, user_in: UserUpdate) -> User:
        """Updates an existing user.

        Args:
            user_id: The ID of the user to update.
            user_in: The data to update the user with. Pydantic model validation handles password complexity if password is provided.

        Returns:
            The updated user object.

        Raises:
            UserNotFoundError: If the user with the given ID is not found.
            UserAlreadyExistsError: If the email is being changed to one that already exists.
        """
        existing_user = await self.user_repository.get_by_id(user_id)
        if not existing_user:
            raise UserNotFoundError(f"User with id {user_id} not found")

        update_data = user_in.model_dump(exclude_unset=True)

        if "email" in update_data and update_data["email"] != existing_user.email:
            conflicting_user = await self.user_repository.get_by_email(
                update_data["email"]
            )
            if conflicting_user and conflicting_user.id != user_id:
                raise UserAlreadyExistsError(
                    f"A user with email {update_data['email']} already exists"
                )

        # Hash password if it's being updated
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data["password"])
            del update_data["password"]
        elif "hashed_password" in update_data:
            del update_data["hashed_password"]

        updated_user = await self.user_repository.update(id=user_id, obj_in=update_data)
        if updated_user is None:
            # Should ideally not happen due to the initial check, but handles race conditions/DB issues
            raise UserNotFoundError(
                f"User with id {user_id} could not be updated or found after update attempt."
            )
        return updated_user

    async def delete_user(self, user_id: int) -> bool:
        """Deletes a user.

        Args:
            user_id: The ID of the user to delete.

        Returns:
            True if the deletion was successful.

        Raises:
            UserNotFoundError: If the user with the given ID is not found.
            Exception: If the deletion fails unexpectedly after the user was found.
        """
        user_to_delete = await self.user_repository.get_by_id(user_id)
        if not user_to_delete:
            raise UserNotFoundError(f"User with id {user_id} not found")

        success = await self.user_repository.delete(user_id)
        if not success:
            raise Exception(f"Failed to delete user with id {user_id}")
        return success

    async def get_by_email(self, email: str) -> User:
        """Retrieves a user by their email address.

        Args:
            email: The email address of the user to retrieve.

        Returns:
            The user object.

        Raises:
            UserNotFoundError: If the user with the given email is not found.
        """
        user = await self.user_repository.get_by_email(email)
        if not user:
            raise UserNotFoundError(f"User with email {email} not found")

        return User(id=user.id, name=user.name, email=user.email)

    async def authenticate(self, email: str, password: str) -> dict:
        """Authenticates a user based on email and password.

        Args:
            email: The user's email address.
            password: The user's password.

        Returns:
            A dictionary containing the access token, token type, and user object.

        Raises:
            AuthenticationError: If the email/password combination is incorrect.
        """
        user_in_db = await self.user_repository.get_by_email(email)
        if not user_in_db or not verify_password(password, user_in_db.hashed_password):
            raise AuthenticationError("Incorrect email or password")

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=str(user_in_db.id), expires_delta=access_token_expires
        )

        user = User(id=user_in_db.id, name=user_in_db.name, email=user_in_db.email)
        return {"access_token": access_token, "token_type": "bearer", "user": user}
