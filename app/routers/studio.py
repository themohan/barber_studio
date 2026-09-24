from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Dict, Any

from app.database import get_db
from app.models import Booking, Order, Product, User, Slot
from app.deps import require_admin
from app.config import settings

router = APIRouter(prefix="/api/studio", tags=["Studio Info & Admin Stats"])

@router.get("/info")
async def get_studio_info():
    return {
        "name": settings.STUDIO_NAME,
        "tagline": settings.STUDIO_TAGLINE,
        "address": settings.STUDIO_ADDRESS,
        "phone": settings.STUDIO_PHONE,
        "email": settings.STUDIO_EMAIL,
        "maps_url": settings.STUDIO_MAPS_URL,
        "hours": [
            {"day": "Monday", "hours": "Closed", "is_open": False},
            {"day": "Tuesday", "hours": "11:00 AM – 6:00 PM", "is_open": True},
            {"day": "Wednesday", "hours": "11:00 AM – 6:00 PM", "is_open": True},
            {"day": "Thursday", "hours": "9:00 AM – 7:00 PM", "is_open": True},
            {"day": "Friday", "hours": "9:00 AM – 7:00 PM", "is_open": True},
            {"day": "Saturday", "hours": "9:00 AM – 5:00 PM", "is_open": True},
            {"day": "Sunday", "hours": "9:00 AM – 5:00 PM", "is_open": True}
        ],
        "policies": [
            {
                "title": "Punctuality & Grace Period",
                "desc": "A $10 fee applies if you are 15+ minutes late. Rescheduling is required if 30+ minutes late."
            },
            {
                "title": "Clean Hair Policy",
                "desc": "Hair must be clean and freshly shampooed prior to cut, or a luxury shampoo service can be added."
            },
            {
                "title": "After-Hours VIP Experience",
                "desc": "$50 after-hours fee applies for requested slots outside standard operating hours."
            },
            {
                "title": "Accepted Payment Methods",
                "desc": "Cash, Zelle, Cash App, and major credit cards accepted at studio checkout."
            }
        ]
    }

@router.get("/stats")
async def get_admin_stats(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    # Total customers
    cust_res = await db.execute(select(func.count(User.id)).where(User.role == "customer"))
    total_customers = cust_res.scalar() or 0

    # Total bookings
    book_res = await db.execute(select(func.count(Booking.id)))
    total_bookings = book_res.scalar() or 0

    # Upcoming bookings (confirmed)
    up_res = await db.execute(select(func.count(Booking.id)).where(Booking.status == "confirmed"))
    upcoming_bookings = up_res.scalar() or 0

    # Bookings revenue
    b_rev_res = await db.execute(
        select(func.sum(Booking.total_price)).where(Booking.status.in_(["confirmed", "completed"]))
    )
    bookings_revenue = b_rev_res.scalar() or 0.0

    # Total orders
    ord_res = await db.execute(select(func.count(Order.id)))
    total_orders = ord_res.scalar() or 0

    # Pending orders
    pend_ord_res = await db.execute(select(func.count(Order.id)).where(Order.status == "pending"))
    pending_orders = pend_ord_res.scalar() or 0

    # Orders revenue
    o_rev_res = await db.execute(
        select(func.sum(Order.total_amount)).where(Order.status != "cancelled")
    )
    orders_revenue = o_rev_res.scalar() or 0.0

    # Products count & low stock
    prod_res = await db.execute(select(func.count(Product.id)).where(Product.is_active == True))
    total_products = prod_res.scalar() or 0

    low_stock_res = await db.execute(
        select(Product).where(and_(Product.is_active == True, Product.stock <= 5))
    )
    low_stock_products = [
        {"id": p.id, "name": p.name, "stock": p.stock}
        for p in low_stock_res.scalars().all()
    ]

    return {
        "total_revenue": round(bookings_revenue + orders_revenue, 2),
        "bookings_revenue": round(bookings_revenue, 2),
        "orders_revenue": round(orders_revenue, 2),
        "total_customers": total_customers,
        "total_bookings": total_bookings,
        "upcoming_bookings": upcoming_bookings,
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "total_products": total_products,
        "low_stock_products": low_stock_products
    }
