"""
Dependency injection utilities for FastAPI.
"""
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.core.database import get_database
from app.core.security import decode_token, TokenData
from app.repositories.user import UserRepository
from app.repositories.booking import BookingRepository
from app.schemas.user import UserInDB, UserRole


# Security scheme
security = HTTPBearer(auto_error=False)


async def get_user_repository(
    client: AsyncIOMotorClient = Depends(get_database)
) -> UserRepository:
    """Get user repository instance."""
    database = client[settings.MONGODB_DB_NAME]
    return UserRepository(database)


async def get_booking_repository(
    client: AsyncIOMotorClient = Depends(get_database)
) -> BookingRepository:
    """Get booking repository instance."""
    database = client[settings.MONGODB_DB_NAME]
    return BookingRepository(database)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    user_repo: UserRepository = Depends(get_user_repository)
) -> UserInDB:
    """Get current authenticated user from JWT token."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    token_data = decode_token(token)
    
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await user_repo.get_by_id(token_data.user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )

    return user


async def get_current_active_user(
    current_user: UserInDB = Depends(get_current_user)
) -> UserInDB:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_current_admin(
    current_user: UserInDB = Depends(get_current_user)
) -> UserInDB:
    """Get current user and verify admin role."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    user_repo: UserRepository = Depends(get_user_repository)
) -> Optional[UserInDB]:
    """Get current user if authenticated, None otherwise."""
    if credentials is None:
        return None

    token = credentials.credentials
    token_data = decode_token(token)
    
    if token_data is None:
        return None

    return await user_repo.get_by_id(token_data.user_id)
