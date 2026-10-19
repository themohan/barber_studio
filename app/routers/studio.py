from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, cast, Date, String
from sqlalchemy.orm import selectinload
from typing import Dict, Any, Optional
from datetime import datetime, timedelta, timezone, date as date_type
import calendar

from app.database import get_db
from app.models import Booking, Order, Product, User, Slot, Service, OrderItem
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

@router.get("/analytics")
async def get_admin_analytics(
    period: str = Query("weekly", description="daily | weekly | monthly"),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns analytics data for admin dashboard charts.
    period: "daily" (last 7 days), "weekly" (last 8 weeks), "monthly" (last 12 months)
    """
    now = datetime.now(timezone.utc)

    # Build date buckets
    if period == "daily":
        num_buckets = 7
        labels = []
        bucket_dates = []
        for i in range(num_buckets - 1, -1, -1):
            d = (now - timedelta(days=i)).date()
            labels.append(d.strftime("%a %b %d"))
            bucket_dates.append(d)

        def get_bucket(dt):
            return dt.date() if hasattr(dt, 'date') else dt

        def label_for(d):
            return d.strftime("%a %b %d")

    elif period == "weekly":
        num_buckets = 8
        labels = []
        bucket_dates = []
        for i in range(num_buckets - 1, -1, -1):
            week_start = (now - timedelta(weeks=i)).date()
            # start of that week (Monday)
            week_start = week_start - timedelta(days=week_start.weekday())
            bucket_dates.append(week_start)
            labels.append(week_start.strftime("Wk %b %d"))

        def get_bucket(dt):
            d = dt.date() if hasattr(dt, 'date') else dt
            return d - timedelta(days=d.weekday())

        def label_for(d):
            return d.strftime("Wk %b %d")

    else:  # monthly
        num_buckets = 12
        labels = []
        bucket_dates = []
        for i in range(num_buckets - 1, -1, -1):
            # Go back i months
            month_dt = now.date().replace(day=1)
            for _ in range(i):
                month_dt = (month_dt - timedelta(days=1)).replace(day=1)
            bucket_dates.append(month_dt)
            labels.append(month_dt.strftime("%b %Y"))

        def get_bucket(dt):
            d = dt.date() if hasattr(dt, 'date') else dt
            return d.replace(day=1)

        def label_for(d):
            return d.strftime("%b %Y")

    # Date range: from earliest bucket to now
    start_date = bucket_dates[0]

    # ---- Revenue Trend (bookings + orders) ----
    booking_res = await db.execute(
        select(Booking).options(selectinload(Booking.slot))
        .where(
            and_(
                Booking.status.in_(["confirmed", "completed"]),
                Booking.created_at >= datetime.combine(start_date, datetime.min.time()).replace(tzinfo=timezone.utc)
            )
        )
    )
    bookings = booking_res.scalars().all()

    order_res = await db.execute(
        select(Order)
        .where(
            and_(
                Order.status != "cancelled",
                Order.created_at >= datetime.combine(start_date, datetime.min.time()).replace(tzinfo=timezone.utc)
            )
        )
    )
    orders = order_res.scalars().all()

    # Build bucket maps
    booking_rev_map = {d: 0.0 for d in bucket_dates}
    for b in bookings:
        created = b.created_at
        if created and created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        if created:
            bucket = get_bucket(created)
            if bucket in booking_rev_map:
                booking_rev_map[bucket] += b.total_price or 0.0

    order_rev_map = {d: 0.0 for d in bucket_dates}
    for o in orders:
        created = o.created_at
        if created and created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        if created:
            bucket = get_bucket(created)
            if bucket in order_rev_map:
                order_rev_map[bucket] += o.total_amount or 0.0

    booking_revenue_series = [round(booking_rev_map[d], 2) for d in bucket_dates]
    order_revenue_series = [round(order_rev_map[d], 2) for d in bucket_dates]
    total_revenue_series = [round(booking_rev_map[d] + order_rev_map[d], 2) for d in bucket_dates]

    # ---- Booking Count Trend ----
    booking_count_map = {d: 0 for d in bucket_dates}
    for b in bookings:
        created = b.created_at
        if created and created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        if created:
            bucket = get_bucket(created)
            if bucket in booking_count_map:
                booking_count_map[bucket] += 1
    booking_count_series = [booking_count_map[d] for d in bucket_dates]

    # ---- Booking Status Breakdown (all time filtered) ----
    status_res = await db.execute(
        select(Booking.status, func.count(Booking.id))
        .group_by(Booking.status)
    )
    booking_status_raw = status_res.all()
    booking_status = {row[0]: row[1] for row in booking_status_raw}

    # ---- Order Status Breakdown ----
    ord_status_res = await db.execute(
        select(Order.status, func.count(Order.id))
        .group_by(Order.status)
    )
    order_status_raw = ord_status_res.all()
    order_status = {row[0]: row[1] for row in order_status_raw}

    # ---- Top 5 Services by Revenue ----
    svc_res = await db.execute(
        select(Service.title, func.sum(Booking.total_price).label("rev"), func.count(Booking.id).label("cnt"))
        .join(Booking, Booking.service_id == Service.id)
        .where(Booking.status.in_(["confirmed", "completed"]))
        .group_by(Service.id, Service.title)
        .order_by(func.sum(Booking.total_price).desc())
        .limit(5)
    )
    top_services = [
        {"name": row[0], "revenue": round(row[1] or 0, 2), "count": row[2]}
        for row in svc_res.all()
    ]

    # ---- Service Category Revenue Split ----
    cat_res = await db.execute(
        select(Service.category, func.sum(Booking.total_price).label("rev"))
        .join(Booking, Booking.service_id == Service.id)
        .where(Booking.status.in_(["confirmed", "completed"]))
        .group_by(Service.category)
        .order_by(func.sum(Booking.total_price).desc())
    )
    category_revenue = [
        {"category": row[0], "revenue": round(row[1] or 0, 2)}
        for row in cat_res.all()
    ]

    # ---- Order Count Trend ----
    order_count_map = {d: 0 for d in bucket_dates}
    for o in orders:
        created = o.created_at
        if created and created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        if created:
            bucket = get_bucket(created)
            if bucket in order_count_map:
                order_count_map[bucket] += 1
    order_count_series = [order_count_map[d] for d in bucket_dates]

    # ---- New Customers Trend ----
    cust_res = await db.execute(
        select(User)
        .where(
            and_(
                User.role == "customer",
                User.created_at >= datetime.combine(start_date, datetime.min.time()).replace(tzinfo=timezone.utc)
            )
        )
    )
    customers = cust_res.scalars().all()
    cust_map = {d: 0 for d in bucket_dates}
    for c in customers:
        created = c.created_at
        if created and created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        if created:
            bucket = get_bucket(created)
            if bucket in cust_map:
                cust_map[bucket] += 1
    customer_series = [cust_map[d] for d in bucket_dates]

    return {
        "period": period,
        "labels": labels,
        "revenue": {
            "total": total_revenue_series,
            "bookings": booking_revenue_series,
            "orders": order_revenue_series
        },
        "booking_counts": booking_count_series,
        "order_counts": order_count_series,
        "new_customers": customer_series,
        "booking_status_breakdown": booking_status,
        "order_status_breakdown": order_status,
        "top_services": top_services,
        "category_revenue": category_revenue
    }

