
import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from mongomock_motor import AsyncMongoMockClient

from app.main import app
from app.core.database import get_database
from app.core.config import settings
from app.core.security import create_access_token
from app.schemas.user import UserRole


@pytest_asyncio.fixture
async def mock_client():
    """Mock MongoDB client shared across requests in a test."""
    return AsyncMongoMockClient()


@pytest_asyncio.fixture
async def mock_db(mock_client):
    """Mock MongoDB database."""
    return mock_client[settings.MONGODB_DB_NAME]


@pytest_asyncio.fixture(autouse=True)
async def app_dependency_overrides(mock_client):
    """Override database dependency for all tests."""
    app.dependency_overrides[get_database] = lambda: mock_client
    yield # Run tests
    app.dependency_overrides = {}


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client for testing."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_user_data():
    return {
        "email": "test@example.com",
        "password": "Password123",
        "full_name": "Test User"
    }


@pytest.fixture
def test_admin_data():
    return {
        "email": "admin@example.com",
        "password": "AdminPassword123",
        "full_name": "Admin User"
    }


from bson import ObjectId

@pytest_asyncio.fixture
async def user_token(test_user_data, mock_db):
    """Create valid user token and insert user into DB."""
    # Insert user to ensure get_current_user succeeds
    user_id = str(ObjectId())
    await mock_db.users.insert_one({
        "_id": user_id,
        "email": test_user_data["email"],
        "hashed_password": "hashed_password_123", # Dummy hash
        "full_name": test_user_data["full_name"],
        "role": UserRole.USER.value,
        "is_active": True,
        "is_verified": True
    })
    
    return create_access_token(
        data={"sub": user_id, "email": test_user_data["email"], "role": UserRole.USER.value}
    )


@pytest_asyncio.fixture
async def admin_token(test_admin_data, mock_db):
    """Create valid admin token and insert admin into DB."""
    # Insert admin
    admin_id = str(ObjectId())
    await mock_db.users.insert_one({
        "_id": admin_id,
        "email": test_admin_data["email"],
        "hashed_password": "hashed_password_456",
        "full_name": test_admin_data["full_name"],
        "role": UserRole.ADMIN.value,
        "is_active": True,
        "is_verified": True
    })

    return create_access_token(
        data={"sub": admin_id, "email": test_admin_data["email"], "role": UserRole.ADMIN.value}
    )
