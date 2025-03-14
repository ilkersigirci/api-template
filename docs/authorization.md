# Authorization

This document explains the authentication and authorization system implemented in this project.

## Overview

The project uses JWT (JSON Web Tokens) for authentication and authorization. The system follows OAuth2 password flow with bearer tokens.

## Authentication Flow

1. **User Registration**:
   - User submits registration data (name, email, password)
   - System validates the data and creates a new user
   - Password is hashed before storage

2. **User Login**:
   - User submits credentials (email, password)
   - System validates credentials against stored data
   - If valid, system generates a JWT token and returns it to the user

3. **Authenticated Requests**:
   - User includes the JWT token in the Authorization header
   - System validates the token and identifies the user
   - If valid, the request proceeds; otherwise, an error is returned

## Implementation Details

### Token Generation

JWT tokens are generated using the `create_access_token` function in `app/core/security.py`:

```python
def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token for the given subject.
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expire, "sub": str(subject)}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
```

The token includes:
- `sub` (subject): The user ID
- `exp` (expiration time): When the token expires

### Password Handling

Passwords are handled securely using the `passlib` library:

```python
# Hashing a password
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Verifying a password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

### Authentication Endpoints

The API provides endpoints for authentication in `app/api/v1/endpoints/auth.py`:

1. **Login Endpoint**:
   - Path: `/api/v1/auth/login`
   - Method: POST
   - Accepts username (email) and password
   - Returns a JWT token if credentials are valid

2. **Registration Endpoint**:
   - Path: `/api/v1/auth/register`
   - Method: POST
   - Accepts user registration data
   - Creates a new user and returns user information

3. **Token Test Endpoint**:
   - Path: `/api/v1/auth/test-token`
   - Method: POST
   - Requires authentication
   - Returns current user information if token is valid

### Token Validation

Token validation is implemented as a dependency in `app/dependencies/auth.py`:

```python
def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)

        if token_data.sub is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    except (JWTError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    user = user_service.get_user(int(token_data.sub))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user
```

This dependency:
1. Extracts the token from the request
2. Decodes and validates the token
3. Retrieves the user based on the subject in the token
4. Returns the user or raises an appropriate exception

### Usage in Endpoints

Protected endpoints use the `get_current_user` dependency to ensure that requests are authenticated:

```python
@router.get("/me", response_model=User)
async def read_current_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Get current user information.
    """
    return current_user
```

## Configuration

Authentication settings are defined in `app/core/config.py`:

- `SECRET_KEY`: Used for signing JWT tokens
- `ALGORITHM`: Algorithm used for JWT token signing (HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time in minutes

These settings can be overridden using environment variables.

## Security Considerations

1. **Token Expiration**: Tokens have a limited lifetime defined by `ACCESS_TOKEN_EXPIRE_MINUTES`.

2. **Secure Password Storage**: Passwords are hashed using bcrypt before storage.

3. **HTTPS**: In production, all API endpoints should be served over HTTPS to prevent token interception.

4. **Secret Key**: The `SECRET_KEY` should be kept secure and changed in production environments.

## Possible Enhancements

1. **Refresh Tokens**: Implement refresh tokens to allow obtaining new access tokens without re-authentication.

2. **Role-Based Access Control**: Add user roles and permissions for more fine-grained access control.

3. **Token Revocation**: Implement a mechanism to revoke tokens before they expire.

4. **Multi-Factor Authentication**: Add support for two-factor authentication.
