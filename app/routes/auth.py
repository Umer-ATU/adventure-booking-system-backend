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


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    user_repo: UserRepository = Depends(get_user_repository)
):
    """
    Register a new user account.
    
    - **email**: Unique email address
    - **full_name**: User's full name
    - **password**: Password (min 8 chars, must contain uppercase, lowercase, digit)
    - **phone**: Optional phone number
    """
    # Check if email already exists
    if await user_repo.email_exists(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    user = await user_repo.create(user_data)
    return user



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



@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    password_data: PasswordChange,
    current_user: UserInDB = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """
    Change current user's password.
    
    - **current_password**: Current password for verification
    - **new_password**: New password (min 8 characters)
    """
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    await user_repo.update_password(current_user.id, password_data.new_password)
    return None


@router.post("/admin/create", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_admin_user(
    user_data: UserCreate,
    current_user: UserInDB = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """
    Create a new admin user. Only existing admins can create new admins.
    
    - **email**: Admin email address
    - **full_name**: Admin's full name
    - **password**: Password
    """
    # Only admins can create admins
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create admin accounts"
        )

    if await user_repo.email_exists(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    user = await user_repo.create(user_data, role=UserRole.ADMIN)
    return user


@router.get("/admin/users", response_model=list[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    role: str = None,
    current_user: UserInDB = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """
    List all users. Admin only.
    
    - **skip**: Number of users to skip
    - **limit**: Max users to return
    - **role**: Filter by role (user/admin)
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    role_filter = UserRole(role) if role else None
    users = await user_repo.get_all(skip=skip, limit=limit, role=role_filter)
    return users


@router.patch("/admin/users/{user_id}/toggle-active", response_model=UserResponse)
async def toggle_user_active(
    user_id: str,
    current_user: UserInDB = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """
    Toggle user active status. Admin only.
    Cannot deactivate yourself.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_active:
        await user_repo.deactivate(user_id)
    else:
        # Reactivate - need to add this method or use update
        from app.schemas.user import UserUpdate
        await user_repo.update(user_id, UserUpdate())
        await user_repo.collection.update_one(
            {"_id": user_id},
            {"$set": {"is_active": True}}
        )
    
    return await user_repo.get_by_id(user_id)
