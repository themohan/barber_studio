from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models import Slot, User
from app.schemas import SlotCreate, SlotBatchCreate, SlotOut, SlotToggleBlock
from app.deps import require_admin
from app.websocket_manager import ws_manager

router = APIRouter(prefix="/api/slots", tags=["Slots"])

@router.get("", response_model=List[SlotOut])
async def list_slots(
    date: Optional[str] = None,
    include_booked: bool = True,
    db: AsyncSession = Depends(get_db)
):
    query = select(Slot)
    if date:
        query = query.where(Slot.date == date)
    if not include_booked:
        query = query.where(and_(Slot.is_booked == False, Slot.is_blocked == False))

    query = query.order_by(Slot.date.asc(), Slot.start_time.asc())
    result = await db.execute(query)
    slots = result.scalars().all()
    return [SlotOut.model_validate(s) for s in slots]

@router.post("/batch", response_model=List[SlotOut], status_code=status.HTTP_201_CREATED)
async def release_slots_batch(
    batch: SlotBatchCreate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Admin slot release engine:
    Generates time slots between start_time and end_time (e.g. 09:00 to 18:00 with 45m interval)
    """
    try:
        t_start = datetime.strptime(batch.start_time, "%H:%M")
        t_end = datetime.strptime(batch.end_time, "%H:%M")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM in 24-hour format.")

    if t_start >= t_end:
        raise HTTPException(status_code=400, detail="Start time must be before end time.")

    delta = timedelta(minutes=batch.interval_minutes)
    current = t_start
    created_slots = []

    # Get existing slots for the date to avoid duplicate overlapping slots
    existing_res = await db.execute(select(Slot).where(Slot.date == batch.date))
    existing_slots = existing_res.scalars().all()
    existing_times = {s.start_time for s in existing_slots}

    while current + delta <= t_end:
        slot_start_str = current.strftime("%H:%M")
        slot_end_str = (current + delta).strftime("%H:%M")

        if slot_start_str not in existing_times:
            new_slot = Slot(
                date=batch.date,
                start_time=slot_start_str,
                end_time=slot_end_str,
                barber_name=batch.barber_name or "Master Barber",
                is_booked=False,
                is_blocked=False
            )
            db.add(new_slot)
            created_slots.append(new_slot)

        current += delta

    if created_slots:
        await db.commit()
        for s in created_slots:
            await db.refresh(s)

        # Broadcast real-time event to all connected customers & admin
        await ws_manager.broadcast({
            "type": "SLOTS_RELEASED",
            "date": batch.date,
            "count": len(created_slots),
            "message": f"New appointment slots released for {batch.date}!"
        })

    return [SlotOut.model_validate(s) for s in created_slots]

@router.post("", response_model=SlotOut, status_code=status.HTTP_201_CREATED)
async def create_single_slot(
    slot_in: SlotCreate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    # Check duplicate
    dup_res = await db.execute(
        select(Slot).where(
            and_(Slot.date == slot_in.date, Slot.start_time == slot_in.start_time)
        )
    )
    if dup_res.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="A slot at this time already exists.")

    new_slot = Slot(
        date=slot_in.date,
        start_time=slot_in.start_time,
        end_time=slot_in.end_time,
        barber_name=slot_in.barber_name or "Master Barber",
        is_booked=False,
        is_blocked=False
    )
    db.add(new_slot)
    await db.commit()
    await db.refresh(new_slot)

    await ws_manager.broadcast({
        "type": "SLOT_CREATED",
        "slot": SlotOut.model_validate(new_slot).model_dump(mode="json")
    })

    return SlotOut.model_validate(new_slot)

@router.patch("/{slot_id}/block", response_model=SlotOut)
async def toggle_block_slot(
    slot_id: int,
    block_in: SlotToggleBlock,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(Slot).where(Slot.id == slot_id))
    slot = res.scalar_one_or_none()
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found.")

    slot.is_blocked = block_in.is_blocked
    await db.commit()
    await db.refresh(slot)

    await ws_manager.broadcast({
        "type": "SLOT_UPDATED",
        "slot_id": slot.id,
        "is_blocked": slot.is_blocked,
        "is_booked": slot.is_booked
    })

    return SlotOut.model_validate(slot)

@router.delete("/{slot_id}")
async def delete_slot(
    slot_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(Slot).where(Slot.id == slot_id))
    slot = res.scalar_one_or_none()
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found.")

    if slot.is_booked:
        raise HTTPException(status_code=400, detail="Cannot delete a booked slot. Cancel the booking first.")

    await db.delete(slot)
    await db.commit()

    await ws_manager.broadcast({
        "type": "SLOT_DELETED",
        "slot_id": slot_id
    })

    return {"message": "Slot deleted successfully."}
