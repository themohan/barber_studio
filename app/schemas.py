from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

# ================= AUTH & USER =================
class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    phone: Optional[str] = None
    role: Optional[str] = "customer"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    phone: Optional[str] = None
    role: str
    created_at: Optional[datetime] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

# ================= SERVICES =================
class ServiceBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=150)
    category: str = "Haircuts"
    description: str
    duration_minutes: int = Field(default=45, ge=10, le=240)
    price: float = Field(default=45.0, ge=0.0)
    image_url: Optional[str] = None

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    duration_minutes: Optional[int] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None

class ServiceOut(ServiceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: Optional[datetime] = None

# ================= SLOTS =================
class SlotCreate(BaseModel):
    date: str  # YYYY-MM-DD
    start_time: str  # HH:MM
    end_time: str    # HH:MM
    barber_name: Optional[str] = "Master Barber"

class SlotBatchCreate(BaseModel):
    date: str  # YYYY-MM-DD
    start_time: str  # HH:MM e.g. "09:00"
    end_time: str    # HH:MM e.g. "17:00"
    interval_minutes: int = Field(default=45, ge=15, le=120)
    barber_name: Optional[str] = "Master Barber"

class SlotOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: str
    start_time: str
    end_time: str
    barber_name: str
    is_booked: bool
    is_blocked: bool
    created_at: Optional[datetime] = None

class SlotToggleBlock(BaseModel):
    is_blocked: bool

# ================= BOOKINGS =================
class BookingCreate(BaseModel):
    slot_id: int
    service_id: int
    customer_notes: Optional[str] = None

class BookingStatusUpdate(BaseModel):
    status: str  # confirmed, completed, cancelled, no-show

class BookingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    slot_id: int
    service_id: int
    status: str
    customer_notes: Optional[str] = None
    total_price: float
    created_at: Optional[datetime] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    user_phone: Optional[str] = None
    service_title: Optional[str] = None
    service_duration: Optional[int] = None
    slot_date: Optional[str] = None
    slot_start_time: Optional[str] = None
    slot_end_time: Optional[str] = None
    barber_name: Optional[str] = None

# ================= REVIEWS =================
class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field(..., min_length=2, max_length=1000)

class ReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    user_id: int
    user_name: str
    rating: int
    comment: str
    created_at: Optional[datetime] = None

# ================= PRODUCTS =================
class ProductBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    category: str = "Hair Styling"
    description: str
    price: float = Field(..., ge=0.0)
    stock: int = Field(default=20, ge=0)
    image_url: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None

class ProductOut(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: Optional[datetime] = None
    average_rating: float = 5.0
    reviews_count: int = 0
    reviews: Optional[List[ReviewOut]] = []

# ================= ORDERS =================
class OrderItemInput(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1)

class OrderCreate(BaseModel):
    items: List[OrderItemInput] = Field(..., min_length=1)
    delivery_type: str = "studio_pickup"  # "studio_pickup" or "delivery"
    shipping_address: Optional[str] = None
    contact_phone: Optional[str] = None
    payment_method: str = "Cash on Arrival"  # "Cash on Arrival", "Zelle", "Card Placeholder", "Apple Pay / Cash App"
    notes: Optional[str] = None

class OrderStatusUpdate(BaseModel):
    status: Optional[str] = None
    payment_status: Optional[str] = None

class OrderItemOut(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: float

class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    total_amount: float
    status: str
    delivery_type: str
    shipping_address: Optional[str] = None
    contact_phone: Optional[str] = None
    payment_method: str
    payment_status: str
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    items: List[OrderItemOut] = []
