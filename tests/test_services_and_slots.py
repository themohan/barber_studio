import pytest
import uuid
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_list_services_public(client: AsyncClient):
    response = await client.get("/api/services")
    assert response.status_code == 200
    services = response.json()
    assert len(services) >= 5
    assert any("VIP" in s["title"] for s in services)

@pytest.mark.asyncio
async def test_admin_create_service(client: AsyncClient, admin_token: str):
    payload = {
        "title": f"Master Beard Dye & Sculpt {uuid.uuid4().hex[:4]}",
        "category": "Beard Care",
        "description": "Semi-permanent beard color enhancement and precision sculpting.",
        "duration_minutes": 35,
        "price": 50.0,
        "image_url": "https://example.com/beard.jpg"
    }
    response = await client.post("/api/services", json=payload, headers={
        "Authorization": f"Bearer {admin_token}"
    })
    assert response.status_code == 201
    data = response.json()
    assert "Master Beard Dye & Sculpt" in data["title"]
    assert data["price"] == 50.0

@pytest.mark.asyncio
async def test_customer_cannot_create_service(client: AsyncClient, customer_token: str):
    payload = {
        "title": "Unauthorized Service",
        "category": "Haircuts",
        "description": "Should fail",
        "duration_minutes": 30,
        "price": 20.0
    }
    response = await client.post("/api/services", json=payload, headers={
        "Authorization": f"Bearer {customer_token}"
    })
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_admin_batch_release_slots(client: AsyncClient, admin_token: str):
    test_date = f"2027-01-{(uuid.uuid4().int % 25) + 1:02d}"
    payload = {
        "date": test_date,
        "start_time": "10:00",
        "end_time": "13:00",
        "interval_minutes": 60,
        "barber_name": "Master Barber Marcus"
    }
    response = await client.post("/api/slots/batch", json=payload, headers={
        "Authorization": f"Bearer {admin_token}"
    })
    assert response.status_code == 201
    slots = response.json()
    assert len(slots) == 3
    assert slots[0]["start_time"] == "10:00"
    assert slots[1]["start_time"] == "11:00"
    assert slots[2]["start_time"] == "12:00"

    # List slots by date
    list_res = await client.get(f"/api/slots?date={test_date}")
    assert list_res.status_code == 200
    assert len(list_res.json()) == 3
