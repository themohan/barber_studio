from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.database import get_db
from app.models import Service, User
from app.schemas import ServiceCreate, ServiceUpdate, ServiceOut
from app.deps import require_admin, get_optional_user
from app.websocket_manager import ws_manager

router = APIRouter(prefix="/api/services", tags=["Services"])

@router.get("", response_model=List[ServiceOut])
async def list_services(
    category: Optional[str] = None,
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db)
):
    query = select(Service)
    if not include_inactive:
        query = query.where(Service.is_active == True)
    if category and category.lower() != "all":
        query = query.where(Service.category == category)
    query = query.order_by(Service.price.asc())

    result = await db.execute(query)
    services = result.scalars().all()
    return [ServiceOut.model_validate(s) for s in services]

@router.get("/{service_id}", response_model=ServiceOut)
async def get_service(service_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found.")
    return ServiceOut.model_validate(service)

@router.post("", response_model=ServiceOut, status_code=status.HTTP_201_CREATED)
async def create_service(
    service_in: ServiceCreate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    new_service = Service(
        title=service_in.title.strip(),
        category=service_in.category.strip(),
        description=service_in.description.strip(),
        duration_minutes=service_in.duration_minutes,
        price=service_in.price,
        image_url=service_in.image_url,
        is_active=True
    )
    db.add(new_service)
    await db.commit()
    await db.refresh(new_service)

    # Real-time WebSocket broadcast
    await ws_manager.broadcast({
        "type": "SERVICE_CREATED",
        "service": {
            "id": new_service.id,
            "title": new_service.title,
            "category": new_service.category,
            "price": new_service.price,
            "duration_minutes": new_service.duration_minutes
        }
    })

    return ServiceOut.model_validate(new_service)

@router.put("/{service_id}", response_model=ServiceOut)
async def update_service(
    service_id: int,
    service_in: ServiceUpdate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found.")

    update_data = service_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(service, field, value)

    await db.commit()
    await db.refresh(service)

    # Broadcast update
    await ws_manager.broadcast({
        "type": "SERVICE_UPDATED",
        "service": {
            "id": service.id,
            "title": service.title,
            "price": service.price,
            "is_active": service.is_active
        }
    })

    return ServiceOut.model_validate(service)

@router.delete("/{service_id}")
async def delete_service(
    service_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found.")

    # Soft delete
    service.is_active = False
    await db.commit()

    await ws_manager.broadcast({
        "type": "SERVICE_DELETED",
        "service_id": service_id
    })

    return {"message": "Service successfully deactivated."}
