
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_create_booking(async_client: AsyncClient, user_token):
    """Test creating a booking."""
    response = await async_client.post(
        "/api/bookings/",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "full_name": "Test Customer",
            "email": "test@customer.com",
            "phone": "1234567890",
            "adventure_park": "Risky Rollercoaster",
            "consent": True
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["adventure_park"] == "Risky Rollercoaster"
    assert "_id" in data


async def test_create_booking_missing_consent(async_client: AsyncClient, user_token):
    """Test creating booking without consent."""
    response = await async_client.post(
        "/api/bookings/",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "full_name": "No Consent",
            "email": "noconsent@test.com",
            "phone": "1234567890",
            "adventure_park": "Haunted Mansion",
            "consent": False
        }
    )
    assert response.status_code == 400


async def test_get_bookings_as_user(async_client: AsyncClient, user_token):
    """Test standard user accessing booking list (forbidden)."""
    response = await async_client.get(
        "/api/bookings/",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403


async def test_get_bookings_as_admin(async_client: AsyncClient, admin_token):
    """Test admin accessing booking list."""
    response = await async_client.get(
        "/api/bookings/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_update_booking_as_admin(async_client: AsyncClient, admin_token, user_token):
    """Test admin updating a booking."""
    # Create booking as user
    create_res = await async_client.post(
        "/api/bookings/",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "full_name": "Update Me",
            "email": "update@test.com",
            "phone": "1234567890",
            "adventure_park": "Nightfall Woods",
            "consent": True
        }
    )
    booking_id = create_res.json()["_id"]

    # Update as admin
    response = await async_client.put(
        f"/api/bookings/{booking_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "full_name": "Updated Name"
        }
    )
    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated Name"
