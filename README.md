# 💈 Private Millionaires Barber Studio - Real-Time Web Platform

An end-to-end, full-stack, real-time web application built for **Private Millionaires Barber Studio** located at **1740 E Washington St, Colton, CA 92324**.

---

## 🌟 Key Features

### 1. Customer Registration & Authentication
- Secure JWT-based authentication with bcrypt password hashing.
- Role-Based Access Control (`customer` vs `admin`).
- Quick 1-click test credentials for instant evaluation.

### 2. Product Management (Admin)
- Admin can upload products (hair styling, beard care, skin & face, cologne, tools).
- Image file upload or remote URL support.
- Real-time stock level tracker with low-stock warnings.
- Instant edit/deactivation controls.

### 3. Customer E-Commerce & Verified Reviews
- Category filtering with responsive product grid.
- Product modal with description, ingredients, and verified customer feedback.
- Customer review submission system (1 to 5-star ratings + written feedback).
- Slide-out shopping bag drawer with quantity adjustments.
- Checkout modal with delivery selection (**Studio Pickup in Colton, CA** vs **Doorstep Delivery**).
- Multiple payment placeholder methods (**Cash on Arrival, Zelle to (909) 430-4591, Card, Apple Pay / Cash App**).
- Customer order history tracking.

### 4. Real-Time Slot Booking Engine
- Customers browse available slots released by Master Barbers for upcoming days.
- Interactive date carousel with instant time slot grid.
- Slot selection with duration, barber name, and custom client style notes.
- Instant booking confirmation modal with downloadable `.ics` calendar file.
- Double-booking prevention with instant UI state locking.
- Customer appointment dashboard with cancellation support (auto-frees slot).

### 5. Admin Slot Release Engine & Services Management
- **Batch Slot Generator**: Release appointments across time intervals (e.g. 09:00 to 18:00 with 45-minute intervals).
- Master schedule control: Instant block/unblock for breaks or lunch, delete slot.
- Service management: Add new services with pricing, duration, category, and photo.

### 6. Real-Time WebSocket Architecture (`/ws`)
- Instant bi-directional communication between clients and the server:
  - `SLOTS_RELEASED`: Real-time notification when new slots become available.
  - `SLOT_BOOKED`: Other clients see slots instantly reserved without page refresh.
  - `NEW_BOOKING_NOTIFICATION`: Admin gets instant alerts on new reservations.
  - `NEW_ORDER_NOTIFICATION`: Admin gets live alerts on new product purchases.
  - `PRODUCT_CREATED` / `PRODUCT_UPDATED` / `REVIEW_ADDED`: Live store updates.

### 7. Studio Information & Verification
- **Address**: 1740 East Washington Street, Colton, CA 92324
- **Phone**: (909) 430-4591
- Direct Google Maps routing integration.
- Studio operating hours and etiquette policies.

---

## 🛠 Tech Stack

- **Backend**: Python 3.10+ with FastAPI, SQLAlchemy 2.0, Async SQLite (`aiosqlite`), PyJWT, Bcrypt, WebSockets.
- **Frontend**: Vanilla HTML5, Vanilla CSS3 (Luxury Noir & Brushed Gold Design System), Vanilla JavaScript (Modular ES6 API, WebSocket, Store, Components).
- **Testing**: Pytest & Pytest-AsyncIO with ASGI test client.
- **DevOps**: Docker, Docker Compose, systemd, Nginx reverse proxy configuration.

---

## 🚀 Running Locally

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Run the application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Visit:
- Web App: **http://localhost:8000**
- API Docs: **http://localhost:8000/docs**

---

## 🧪 Running Automated Tests

```bash
source venv/bin/activate
pytest -v
```

All 11 integration and unit tests pass covering auth, services, slots, bookings, products, reviews, and orders.

---

## 🔑 Demo Credentials

| Account | Email | Password | Role |
| :--- | :--- | :--- | :--- |
| **Master Barber (Owner)** | `admin@privatemillionaires.com` | `admin123` | Admin |
| **VIP Client** | `customer@vip.com` | `customer123` | Customer |
