import os
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
from app.database import init_db
from app.websocket_manager import ws_manager
from app.routers import auth, services, slots, bookings, products, orders, uploads, studio
from app.seed import seed_database

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure static dirs exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs("static/images", exist_ok=True)
    
    # Initialize DB tables
    await init_db()
    
    # Auto-seed initial data (Admin, default services, products, upcoming slots)
    await seed_database()
    
    yield

app = FastAPI(
    title=settings.APP_NAME,
    description="Real-Time Web Application for Private Millionaires Barber Studio, Colton CA",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth.router)
app.include_router(services.router)
app.include_router(slots.router)
app.include_router(bookings.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(uploads.router)
app.include_router(studio.router)

# WebSocket Endpoint for real-time live events
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Respond to ping or heartbeats
            try:
                msg = json.loads(data)
                if msg.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except Exception:
                pass
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)

# Mount Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.api_route("/", methods=["GET", "HEAD"])
async def serve_index():
    return FileResponse("static/index.html")

# Health check
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "active_ws_connections": len(ws_manager.active_connections)
    }
