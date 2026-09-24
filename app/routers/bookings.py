import sys
from pathlib import Path

# Ensure project root is in sys.path for direct execution and IDE import resolution
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.database import get_db
from app.models import Booking, Slot, Service, User
from app.schemas import BookingCreate, BookingStatusUpdate, BookingOut
from app.deps import get_current_user, require_admin
from app.websocket_manager import ws_manager

router = APIRouter(prefix="/api/bookings", tags=["Bookings"])

def enrich_booking(b: Booking) -> BookingOut:
    return BookingOut(
        id=b.id,
        user_id=b.user_id,
        slot_id=b.slot_id,
        service_id=b.service_id,
        status=b.status,
        customer_notes=b.customer_notes,
        total_price=b.total_price,
        created_at=b.created_at,
        user_name=b.user.name if b.user else "VIP Client",
        user_email=b.user.email if b.user else "",
        user_phone=b.user.phone if b.user else "",
        service_title=b.service.title if b.service else "Custom Grooming",
        service_duration=b.service.duration_minutes if b.service else 45,
        slot_date=b.slot.date if b.slot else "",
        slot_start_time=b.slot.start_time if b.slot else "",
        slot_end_time=b.slot.end_time if b.slot else "",
        barber_name=b.slot.barber_name if b.slot else "Master Barber"
    )

@router.post("", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_in: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verify slot availability
    slot_res = await db.execute(select(Slot).where(Slot.id == booking_in.slot_id))
    slot = slot_res.scalar_one_or_none()
    if not slot:
        raise HTTPException(status_code=404, detail="Selected slot does not exist.")
    if slot.is_booked:
        raise HTTPException(status_code=400, detail="This slot has already been booked by another client.")
    if slot.is_blocked:
        raise HTTPException(status_code=400, detail="This slot is currently unavailable.")

    # Verify service
    service_res = await db.execute(select(Service).where(Service.id == booking_in.service_id))
    service = service_res.scalar_one_or_none()
    if not service or not service.is_active:
        raise HTTPException(status_code=404, detail="Selected service is not currently available.")

    # Reserve slot
    slot.is_booked = True

    new_booking = Booking(
        user_id=current_user.id,
        slot_id=slot.id,
        service_id=service.id,
        status="confirmed",
        customer_notes=booking_in.customer_notes.strip() if booking_in.customer_notes else None,
        total_price=service.price
    )
    db.add(new_booking)
    await db.commit()
    await db.refresh(new_booking)

    # Load relationships for response and broadcast
    query = (
        select(Booking)
        .options(
            selectinload(Booking.user),
            selectinload(Booking.slot),
            selectinload(Booking.service)
        )
        .where(Booking.id == new_booking.id)
    )
    b_res = await db.execute(query)
    full_booking = b_res.scalar_one()

    enriched = enrich_booking(full_booking)

    # Broadcast real-time slot update to all clients
    await ws_manager.broadcast({
        "type": "SLOT_BOOKED",
        "slot_id": slot.id,
        "date": slot.date,
        "start_time": slot.start_time,
        "booking_id": full_booking.id,
        "service_title": service.title,
        "client_name": current_user.name
    })

    # Broadcast admin notification
    await ws_manager.broadcast({
        "type": "NEW_BOOKING_NOTIFICATION",
        "booking": enriched.model_dump(mode="json")
    })

    return enriched

@router.get("/my", response_model=List[BookingOut])
async def get_my_bookings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(Booking)
        .options(
            selectinload(Booking.user),
            selectinload(Booking.slot),
            selectinload(Booking.service)
        )
        .where(Booking.user_id == current_user.id)
        .order_by(Booking.created_at.desc())
    )
    res = await db.execute(query)
    bookings = res.scalars().all()
    return [enrich_booking(b) for b in bookings]

@router.get("/all", response_model=List[BookingOut])
async def get_all_bookings(
    date: Optional[str] = None,
    status_filter: Optional[str] = None,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(Booking)
        .options(
            selectinload(Booking.user),
            selectinload(Booking.slot),
            selectinload(Booking.service)
        )
    )
    if status_filter and status_filter.lower() != "all":
        query = query.where(Booking.status == status_filter)

    query = query.order_by(Booking.created_at.desc())
    res = await db.execute(query)
    bookings = res.scalars().all()

    if date:
        bookings = [b for b in bookings if b.slot and b.slot.date == date]

    return [enrich_booking(b) for b in bookings]

@router.patch("/{booking_id}/status", response_model=BookingOut)
async def update_booking_status(
    booking_id: int,
    status_in: BookingStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(Booking)
        .options(
            selectinload(Booking.user),
            selectinload(Booking.slot),
            selectinload(Booking.service)
        )
        .where(Booking.id == booking_id)
    )
    res = await db.execute(query)
    booking = res.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")

    # Permissions: Admin can set any status. Customer can only cancel their own booking.
    if current_user.role != "admin" and booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this booking.")

    if current_user.role != "admin" and status_in.status != "cancelled":
        raise HTTPException(status_code=403, detail="Customers can only cancel appointments.")

    new_status = status_in.status.lower()
    booking.status = new_status

    # If cancelled, free up the slot so other customers can book it!
    if new_status == "cancelled" and booking.slot:
        booking.slot.is_booked = False

    await db.commit()
    await db.refresh(booking)

    enriched = enrich_booking(booking)

    # Real-time broadcast
    await ws_manager.broadcast({
        "type": "BOOKING_STATUS_CHANGED",
        "booking_id": booking.id,
        "status": new_status,
        "slot_id": booking.slot_id,
        "slot_freed": (new_status == "cancelled")
    })

    return enriched
