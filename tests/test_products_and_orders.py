import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_products_reviews_and_orders_flow(client: AsyncClient, admin_token: str, customer_token: str):
    # 1. Admin uploads a product
    new_prod = {
        "name": "Millionaires Gold Infused Beard Butter",
        "category": "Beard Care",
        "description": "Deep conditioning shea and mango butter with subtle amber fragrance.",
        "price": 30.0,
        "stock": 15,
        "image_url": "https://example.com/butter.jpg"
    }
    p_res = await client.post("/api/products", json=new_prod, headers={
        "Authorization": f"Bearer {admin_token}"
    })
    assert p_res.status_code == 201
    prod_data = p_res.json()
    prod_id = prod_data["id"]

    # 2. Customer adds a review
    rev_res = await client.post(f"/api/products/{prod_id}/reviews", json={
        "rating": 5,
        "comment": "Incredible scent and leaves my beard ultra-soft!"
    }, headers={
        "Authorization": f"Bearer {customer_token}"
    })
    assert rev_res.status_code == 201
    rev_data = rev_res.json()
    assert rev_data["rating"] == 5

    # 3. Customer places an order
    order_payload = {
        "items": [
            {"product_id": prod_id, "quantity": 2}
        ],
        "delivery_type": "studio_pickup",
        "payment_method": "Cash on Arrival",
        "contact_phone": "(909) 555-1234",
        "notes": "Pick up during haircut appointment"
    }
    ord_res = await client.post("/api/orders", json=order_payload, headers={
        "Authorization": f"Bearer {customer_token}"
    })
    assert ord_res.status_code == 201
    order_data = ord_res.json()
    assert order_data["total_amount"] == 60.0
    assert order_data["status"] == "pending"

    # 4. Stock should have been deducted (15 - 2 = 13)
    p_check = await client.get(f"/api/products/{prod_id}")
    assert p_check.json()["stock"] == 13

    # 5. Customer views order history
    my_orders = await client.get("/api/orders/my", headers={
        "Authorization": f"Bearer {customer_token}"
    })
    assert my_orders.status_code == 200
    assert any(o["id"] == order_data["id"] for o in my_orders.json())

    # 6. Admin updates order status
    update_res = await client.patch(f"/api/orders/{order_data['id']}/status", json={
        "status": "ready_for_pickup",
        "payment_status": "cash_on_pickup"
    }, headers={
        "Authorization": f"Bearer {admin_token}"
    })
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "ready_for_pickup"
