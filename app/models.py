from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey
)
from sqlalchemy.orm import relationship
from app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(180), unique=True, index=True, nullable=False)
    phone = Column(String(50), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(30), default="customer", nullable=False)  # "customer" or "admin"
    created_at = Column(DateTime, default=utc_now)

    bookings = relationship("Booking", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    category = Column(String(80), nullable=False, default="Haircuts")  # Haircuts, Beard Care, VIP Combos, Skin & Facial, Treatments
    description = Column(Text, nullable=False)
    duration_minutes = Column(Integer, nullable=False, default=45)
    price = Column(Float, nullable=False, default=45.0)
    image_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utc_now)

    bookings = relationship("Booking", back_populates="service")


class Slot(Base):
    __tablename__ = "slots"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String(20), nullable=False, index=True)  # YYYY-MM-DD
    start_time = Column(String(10), nullable=False)        # HH:MM (24h format)
    end_time = Column(String(10), nullable=False)          # HH:MM
    barber_name = Column(String(100), default="Master Barber", nullable=False)
    is_booked = Column(Boolean, default=False, nullable=False)
    is_blocked = Column(Boolean, default=False, nullable=False)  # Admin break/unavailable
    created_at = Column(DateTime, default=utc_now)

    booking = relationship("Booking", back_populates="slot", uselist=False)


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    slot_id = Column(Integer, ForeignKey("slots.id"), nullable=False, unique=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    status = Column(String(30), default="confirmed", nullable=False)  # confirmed, completed, cancelled, no-show
    customer_notes = Column(Text, nullable=True)
    total_price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=utc_now)

    user = relationship("User", back_populates="bookings")
    slot = relationship("Slot", back_populates="booking")
    service = relationship("Service", back_populates="bookings")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    category = Column(String(80), nullable=False, default="Hair Styling")  # Hair Styling, Beard Care, Skin & Face, Cologne & Fragrance, Tools
    description = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=25, nullable=False)
    image_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utc_now)

    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="product")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1 to 5
    comment = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utc_now)

    product = relationship("Product", back_populates="reviews")
    user = relationship("User", back_populates="reviews")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String(40), default="pending", nullable=False)  # pending, processing, ready_for_pickup, shipped, delivered, cancelled
    delivery_type = Column(String(40), default="studio_pickup", nullable=False)  # studio_pickup, delivery
    shipping_address = Column(Text, nullable=True)
    contact_phone = Column(String(50), nullable=True)
    payment_method = Column(String(50), default="Cash on Arrival", nullable=False)  # Cash on Arrival, Zelle, Card Placeholder, Apple Pay
    payment_status = Column(String(30), default="pending", nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    unit_price = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
