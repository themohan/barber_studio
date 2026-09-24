from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.database import get_db
from app.models import Order, OrderItem, Product, User
from app.schemas import (
    OrderCreate, OrderStatusUpdate, OrderOut, OrderItemOut
)
from app.deps import get_current_user, require_admin
from app.websocket_manager import ws_manager

router = APIRouter(prefix="/api/orders", tags=["Orders"])

def enrich_order(o: Order) -> OrderOut:
    items_out = []
    if o.items:
        for it in o.items:
            p_name = it.product.name if it.product else "Grooming Item"
            items_out.append(OrderItemOut(
                id=it.id,
                product_id=it.product_id,
                product_name=p_name,
                quantity=it.quantity,
                unit_price=it.unit_price
            ))
    return OrderOut(
        id=o.id,
        user_id=o.user_id,
        user_name=o.user.name if o.user else "VIP Client",
        user_email=o.user.email if o.user else "",
        total_amount=o.total_amount,
        status=o.status,
        delivery_type=o.delivery_type,
        shipping_address=o.shipping_address,
        contact_phone=o.contact_phone,
        payment_method=o.payment_method,
        payment_status=o.payment_status,
        notes=o.notes,
        created_at=o.created_at,
        items=items_out
    )

@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_in: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not order_in.items:
        raise HTTPException(status_code=400, detail="Order must contain at least one product.")

    total_amount = 0.0
    order_items_to_create = []

    # Validate each product, stock, and calculate total
    for item_input in order_in.items:
        p_res = await db.execute(select(Product).where(Product.id == item_input.product_id))
        product = p_res.scalar_one_or_none()
        if not product or not product.is_active:
            raise HTTPException(
                status_code=400,
                detail=f"Product ID {item_input.product_id} is no longer available."
            )
        if product.stock < item_input.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for {product.name}. Available: {product.stock}"
            )

        # Deduct stock
        product.stock -= item_input.quantity
        line_total = product.price * item_input.quantity
        total_amount += line_total

        order_items_to_create.append({
            "product_id": product.id,
            "quantity": item_input.quantity,
            "unit_price": product.price
        })

    new_order = Order(
        user_id=current_user.id,
        total_amount=round(total_amount, 2),
        status="pending",
        delivery_type=order_in.delivery_type,
        shipping_address=order_in.shipping_address.strip() if order_in.shipping_address else None,
        contact_phone=order_in.contact_phone.strip() if order_in.contact_phone else current_user.phone,
        payment_method=order_in.payment_method,
        payment_status="pending",
        notes=order_in.notes.strip() if order_in.notes else None
    )
    db.add(new_order)
    await db.flush()

    for item_data in order_items_to_create:
        item = OrderItem(
            order_id=new_order.id,
            product_id=item_data["product_id"],
            quantity=item_data["quantity"],
            unit_price=item_data["unit_price"]
        )
        db.add(item)

    await db.commit()

    # Load complete order with relationships
    query = (
        select(Order)
        .options(
            selectinload(Order.user),
            selectinload(Order.items).selectinload(OrderItem.product)
        )
        .where(Order.id == new_order.id)
    )
    res = await db.execute(query)
    full_order = res.scalar_one()

    enriched = enrich_order(full_order)

    # Real-time WebSocket event for admin
    await ws_manager.broadcast({
        "type": "NEW_ORDER_NOTIFICATION",
        "order": enriched.model_dump(mode="json"),
        "message": f"New order #{full_order.id} placed by {current_user.name} for ${enriched.total_amount:.2f}"
    })

    return enriched

@router.get("/my", response_model=List[OrderOut])
async def get_my_orders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(Order)
        .options(
            selectinload(Order.user),
            selectinload(Order.items).selectinload(OrderItem.product)
        )
        .where(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
    )
    res = await db.execute(query)
    orders = res.scalars().all()
    return [enrich_order(o) for o in orders]

@router.get("/all", response_model=List[OrderOut])
async def get_all_orders(
    status_filter: Optional[str] = None,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(Order)
        .options(
            selectinload(Order.user),
            selectinload(Order.items).selectinload(OrderItem.product)
        )
    )
    if status_filter and status_filter.lower() != "all":
        query = query.where(Order.status == status_filter)

    query = query.order_by(Order.created_at.desc())
    res = await db.execute(query)
    orders = res.scalars().all()
    return [enrich_order(o) for o in orders]

@router.patch("/{order_id}/status", response_model=OrderOut)
async def update_order_status(
    order_id: int,
    update_in: OrderStatusUpdate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(Order)
        .options(
            selectinload(Order.user),
            selectinload(Order.items).selectinload(OrderItem.product)
        )
        .where(Order.id == order_id)
    )
    res = await db.execute(query)
    order = res.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    if update_in.status:
        order.status = update_in.status.lower()
    if update_in.payment_status:
        order.payment_status = update_in.payment_status.lower()

    await db.commit()
    await db.refresh(order)

    enriched = enrich_order(order)

    await ws_manager.broadcast({
        "type": "ORDER_STATUS_CHANGED",
        "order_id": order.id,
        "status": order.status,
        "payment_status": order.payment_status
    })

    return enriched
