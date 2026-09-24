import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import init_db
from app.seed import seed_database

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    await init_db()
    await seed_database()

@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

@pytest_asyncio.fixture
async def admin_token(client: AsyncClient):
    response = await client.post("/api/auth/login", json={
        "email": "admin@privatemillionaires.com",
        "password": "admin123"
    })
    assert response.status_code == 200, f"Admin login failed: {response.text}"
    return response.json()["access_token"]

@pytest_asyncio.fixture
async def customer_token(client: AsyncClient):
    response = await client.post("/api/auth/login", json={
        "email": "customer@vip.com",
        "password": "customer123"
    })
    assert response.status_code == 200, f"Customer login failed: {response.text}"
    return response.json()["access_token"]
