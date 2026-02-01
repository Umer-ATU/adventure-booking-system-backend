
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

# Testing with pytest-asyncio
pytestmark = pytest.mark.asyncio

async def test_register_user(async_client: AsyncClient):
    """Test user registration."""
    response = await async_client.post(
        "/api/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "Password123", # Meets all criteria
            "full_name": "New User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "_id" in data
    assert "password" not in data


async def test_login_user(async_client: AsyncClient, mock_db):
    """Test user login."""
    # First register
    await async_client.post(
        "/api/auth/register",
        json={
            "email": "login@example.com",
            "password": "Password123",
            "full_name": "Login User"
        }
    )
    
    # Then login
    response = await async_client.post(
        "/api/auth/login",
        json={
            "email": "login@example.com",
            "password": "Password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


async def test_login_invalid_credentials(async_client: AsyncClient):
    """Test login with wrong password."""
    response = await async_client.post(
        "/api/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "WrongPassword"
        }
    )
    assert response.status_code == 401


async def test_get_current_user_me(async_client: AsyncClient, user_token):
    """Test access to protected /me endpoint."""
    response = await async_client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"


async def test_get_current_user_unauthorized(async_client: AsyncClient):
    """Test access to /me without token."""
    response = await async_client.get("/api/auth/me")
    assert response.status_code == 401 
    # FastAPI SecurityUtils typically returns 401 or 403 depending on if it's missing or invalid.
    # auto_error=False in HTTPBearer might return None credential, 
    # and our code raises 401 if credentials is None.
    # We'll assert 401 based on deps.py logic.
    assert response.status_code == 401
