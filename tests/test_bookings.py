import pytest
import uuid
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_booking_slot_flow(client: AsyncClient, customer_token: str, admin_token: str):
    # 1. Create a fresh test slot with unique random date and time
    unique_suffix = uuid.uuid4().hex[:6]
    test_date = f"2030-01-{(uuid.uuid4().int % 25) + 1:02d}"
    slot_create_res = await client.post("/api/slots", json={
        "date": test_date,
        "start_time": f"{(uuid.uuid4().int % 10) + 10:02d}:{(uuid.uuid4().int % 50):02d}",
        "end_time": "23:59",
        "barber_name": f"Barber {unique_suffix}"
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert slot_create_res.status_code == 201, f"Slot creation failed: {slot_create_res.text}"
    target_slot = slot_create_res.json()

    # 2. Get a service
    svc_res = await client.get("/api/services")
    service = svc_res.json()[0]

    # 3. Customer books the slot
    book_res = await client.post("/api/bookings", json={
        "slot_id": target_slot["id"],
        "service_id": service["id"],
        "customer_notes": "Sharp low taper fade please"
    }, headers={
        "Authorization": f"Bearer {customer_token}"
    })
    assert book_res.status_code == 201
    booking = book_res.json()
    assert booking["status"] == "confirmed"
    assert booking["total_price"] == service["price"]

    # 4. Attempting to book the SAME slot again should fail
    dup_res = await client.post("/api/bookings", json={
        "slot_id": target_slot["id"],
        "service_id": service["id"]
    }, headers={
        "Authorization": f"Bearer {customer_token}"
    })
    assert dup_res.status_code == 400
    assert "already been booked" in dup_res.json()["detail"].lower()

    # 5. Customer checks their appointments
    my_res = await client.get("/api/bookings/my", headers={
        "Authorization": f"Bearer {customer_token}"
    })
    assert my_res.status_code == 200
    my_bookings = my_res.json()
    assert any(b["id"] == booking["id"] for b in my_bookings)

    # 6. Customer cancels booking -> slot should become available again
    cancel_res = await client.patch(f"/api/bookings/{booking['id']}/status", json={
        "status": "cancelled"
    }, headers={
        "Authorization": f"Bearer {customer_token}"
    })
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "cancelled"

    # Verify slot is unbooked
    slot_check = await client.get(f"/api/slots?date={test_date}")
    slot_obj = next(s for s in slot_check.json() if s["id"] == target_slot["id"])
    assert slot_obj["is_booked"] is False
