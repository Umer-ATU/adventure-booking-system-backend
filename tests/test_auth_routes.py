import pytest
from httpx import AsyncClient


@pytest.fixture
def test_reg_user():
    return {
        "email": "brandnewuser@example.com",
        "password": "Password123!",
        "full_name": "New User"
    }


@pytest.mark.asyncio
async def test_register_user_success(async_client: AsyncClient, test_reg_user):
    """Register a brand-new user — should return 201."""
    response = await async_client.post("/api/auth/register", json=test_reg_user)
    assert response.status_code == 201
    data = response.json()
    # The response uses alias _id or a mapped id field
    assert data.get("email") == test_reg_user["email"]


@pytest.mark.asyncio
async def test_register_user_duplicate(async_client: AsyncClient, test_reg_user):
    """Registering the same email twice should return 400."""
    # First registration
    await async_client.post("/api/auth/register", json=test_reg_user)
    # Second registration with same email
    response = await async_client.post("/api/auth/register", json=test_reg_user)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_valid_credentials(async_client: AsyncClient, test_reg_user):
    """After registering, login with correct creds returns a token."""
    await async_client.post("/api/auth/register", json=test_reg_user)

    response = await async_client.post("/api/auth/login", json={
        "email": test_reg_user["email"],
        "password": test_reg_user["password"]
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(async_client: AsyncClient):
    """Login with wrong email/password returns 401."""
    response = await async_client.post("/api/auth/login", json={
        "email": "nobody@example.com",
        "password": "WrongPassword1!"
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_profile(async_client: AsyncClient, user_token: str):
    """Authenticated GET /auth/me returns 200 with user data."""
    response = await async_client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "email" in data


@pytest.mark.asyncio
async def test_get_profile_unauthorized(async_client: AsyncClient):
    """GET /auth/me without token returns 401."""
    response = await async_client.get("/api/auth/me")
    assert response.status_code == 401
