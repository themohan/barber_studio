import pytest
import uuid
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_customer_registration(client: AsyncClient):
    unique_email = f"jordan.{uuid.uuid4().hex[:6]}@example.com"
    payload = {
        "name": "Jordan Bell",
        "email": unique_email,
        "password": "strongPassword123",
        "phone": "(909) 555-4321"
    }
    response = await client.post("/api/auth/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == unique_email
    assert data["user"]["role"] == "customer"

@pytest.mark.asyncio
async def test_duplicate_registration_fails(client: AsyncClient):
    dup_email = f"dup.{uuid.uuid4().hex[:6]}@example.com"
    payload = {
        "name": "Jordan Duplicate",
        "email": dup_email,
        "password": "strongPassword123"
    }
    # First registration
    res1 = await client.post("/api/auth/register", json=payload)
    assert res1.status_code == 200

    # Second registration with same email
    res2 = await client.post("/api/auth/register", json=payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"].lower()

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    response = await client.post("/api/auth/login", json={
        "email": "admin@privatemillionaires.com",
        "password": "admin123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["role"] == "admin"
    assert "access_token" in data

@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient):
    response = await client.post("/api/auth/login", json={
        "email": "admin@privatemillionaires.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_current_user_profile(client: AsyncClient, customer_token: str):
    response = await client.get("/api/auth/me", headers={
        "Authorization": f"Bearer {customer_token}"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "customer@vip.com"
