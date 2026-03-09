import pytest
from httpx import AsyncClient

@pytest.fixture
def adventure_payload():
    return {
        "title": "Test Adventure",
        "description": "A very long description for a test adventure. " * 5,
        "base_price": 99.99,
        "duration_minutes": 180,
        "max_participants": 10,
        "location": "Test Location",
        "category": "outdoor",
        "difficulty": "moderate",
        "inclusions": ["Guide", "Meals"],
        "is_active": True,
        "is_featured": False
    }


@pytest.mark.asyncio
async def test_create_adventure_admin(async_client: AsyncClient, admin_token: str, adventure_payload):
    response = await async_client.post(
        "/api/adventures/",
        json=adventure_payload,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == adventure_payload["title"]
    assert "_id" in data


@pytest.mark.asyncio
async def test_create_adventure_user_forbidden(async_client: AsyncClient, user_token: str, adventure_payload):
    response = await async_client.post(
        "/api/adventures/",
        json=adventure_payload,
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_adventures(async_client: AsyncClient, admin_token: str, adventure_payload):
    # First create
    await async_client.post("/api/adventures/", json=adventure_payload, headers={"Authorization": f"Bearer {admin_token}"})
    
    response = await async_client.get("/api/adventures/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_get_featured_adventures(async_client: AsyncClient, admin_token: str, adventure_payload):
    adv_data = adventure_payload.copy()
    adv_data["is_featured"] = True
    await async_client.post("/api/adventures/", json=adv_data, headers={"Authorization": f"Bearer {admin_token}"})
    
    response = await async_client.get("/api/adventures/featured")
    assert response.status_code == 200
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_get_categories(async_client: AsyncClient, admin_token: str, adventure_payload):
    await async_client.post("/api/adventures/", json=adventure_payload, headers={"Authorization": f"Bearer {admin_token}"})
    response = await async_client.get("/api/adventures/categories")
    assert response.status_code == 200
    data = response.json()
    assert "categories" in data


@pytest.mark.asyncio
async def test_get_single_adventure(async_client: AsyncClient, admin_token: str, adventure_payload):
    res_create = await async_client.post("/api/adventures/", json=adventure_payload, headers={"Authorization": f"Bearer {admin_token}"})
    adv_id = res_create.json()["_id"]
    
    response = await async_client.get(f"/api/adventures/{adv_id}")
    assert response.status_code == 200
    assert response.json()["_id"] == adv_id


@pytest.mark.asyncio
async def test_get_single_adventure_not_found(async_client: AsyncClient):
    response = await async_client.get("/api/adventures/123456789012345678901234")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_adventure(async_client: AsyncClient, admin_token: str, adventure_payload):
    res_create = await async_client.post("/api/adventures/", json=adventure_payload, headers={"Authorization": f"Bearer {admin_token}"})
    adv_id = res_create.json()["_id"]
    
    update_data = {"base_price": 199.99}
    response = await async_client.put(
        f"/api/adventures/{adv_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["base_price"] == 199.99


@pytest.mark.asyncio
async def test_toggle_featured(async_client: AsyncClient, admin_token: str, adventure_payload):
    res_create = await async_client.post("/api/adventures/", json=adventure_payload, headers={"Authorization": f"Bearer {admin_token}"})
    adv_id = res_create.json()["_id"]
    
    response = await async_client.patch(
        f"/api/adventures/{adv_id}/toggle-featured",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["is_featured"] is True


@pytest.mark.asyncio
async def test_toggle_active(async_client: AsyncClient, admin_token: str, adventure_payload):
    res_create = await async_client.post("/api/adventures/", json=adventure_payload, headers={"Authorization": f"Bearer {admin_token}"})
    adv_id = res_create.json()["_id"]
    
    response = await async_client.patch(
        f"/api/adventures/{adv_id}/toggle-active",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["is_active"] is False


@pytest.mark.asyncio
async def test_delete_adventure(async_client: AsyncClient, admin_token: str, adventure_payload):
    res_create = await async_client.post("/api/adventures/", json=adventure_payload, headers={"Authorization": f"Bearer {admin_token}"})
    adv_id = res_create.json()["_id"]
    
    response = await async_client.delete(
        f"/adventures/{adv_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 204
    
    # Check it's gone
    res_get = await async_client.get(f"/adventures/{adv_id}")
    assert res_get.status_code == 404
