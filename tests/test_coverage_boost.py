import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_auth_me(async_client: AsyncClient, user_token: str):
    response = await async_client.get("/api/auth/me", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_auth_me_unauthorized(async_client: AsyncClient):
    response = await async_client.get("/api/auth/me")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_create_payment_intent_unauthorized(async_client: AsyncClient):
    response = await async_client.post("/api/payments/create-intent", json={"booking_id": "123"})
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_payment_webhook_invalid_signature(async_client: AsyncClient):
    response = await async_client.post(
        "/api/webhooks/stripe",
        content=b"empty",
        headers={"Stripe-Signature": "invalid"}
    )
    assert response.status_code == 400
