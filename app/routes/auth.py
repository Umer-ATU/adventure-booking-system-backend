"""
Authentication routes for user registration, login, and token management.
"""
from datetime import timedelta

from fastapi import APIRouter, HTTPException, status, Depends

from app.core.config import settings
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from app.core.deps import get_user_repository, get_current_user
from app.repositories.user import UserRepository
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
    UserInDB,
    Token,
    TokenRefresh,
    PasswordChange,
    UserRole,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    user_repo: UserRepository = Depends(get_user_repository)
):
    """
    Authenticate user and return JWT tokens.
    
    - **email**: User email
    - **password**: User password
    
    Returns access_token and refresh_token.
    """
    user = await user_repo.get_by_email(credentials.email)
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )

    # Create tokens
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email, "role": user.role.value}
    )
    refresh_token = create_refresh_token(
        data={"sub": user.id, "email": user.email, "role": user.role.value}
    )

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh,
    user_repo: UserRepository = Depends(get_user_repository)
):
    """
    Refresh access token using refresh token.
    
    - **refresh_token**: Valid refresh token
    """
    token_info = verify_token(token_data.refresh_token, token_type="refresh")
    
    if not token_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    user = await user_repo.get_by_id(token_info.user_id)
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Create new tokens
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email, "role": user.role.value}
    )
    refresh_token = create_refresh_token(
        data={"sub": user.id, "email": user.email, "role": user.role.value}
    )

    return Token(access_token=access_token, refresh_token=refresh_token)


