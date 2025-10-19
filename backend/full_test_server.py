"""Full backend server with authentication for testing."""

import asyncio
import logging
import random
import sys
from datetime import datetime
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.src.api import auth, health
from backend.src.api import websocket as ws_router
from backend.src.config import get_settings
from backend.src.middleware.error_handler import add_exception_handlers
from backend.src.services.websocket_manager import manager

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="UniFi Network API - Full Test Server",
    version="0.1.0",
    description="Test server with authentication and WebSocket",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handlers
add_exception_handlers(app)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(ws_router.router, prefix="/api", tags=["WebSocket"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "UniFi Network Full Test Server",
        "docs": "/docs",
        "health": "/health",
        "auth": {
            "login": "/api/auth/login",
            "me": "/api/auth/me",
            "users": "/api/auth/users",
        },
        "websocket": "/api/ws",
        "stats": "/api/ws/stats",
    }


# Background task to simulate periodic data
async def simulate_periodic_data():
    """Simulate periodic metric updates."""
    await asyncio.sleep(5)  # Wait for server to start

    while True:
        try:
            # Simulate metrics data
            metrics_data = {
                "type": "metrics",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "total_devices": random.randint(10, 20),
                    "online_devices": random.randint(8, 15),
                    "total_clients": random.randint(20, 50),
                    "avg_latency_ms": round(random.uniform(1.0, 5.0), 2),
                    "total_traffic_mbps": round(random.uniform(50, 200), 2),
                },
            }

            await manager.broadcast_to_room(metrics_data, "metrics")
            count = len(manager.rooms.get("metrics", []))
            if count > 0:
                print(f"📊 Broadcasted metrics to {count} clients")

        except Exception as e:
            print(f"Error broadcasting metrics: {e}")

        await asyncio.sleep(10)  # Broadcast every 10 seconds


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    print("\n" + "=" * 70)
    print("🚀 UniFi Network Full Test Server Starting...")
    print("=" * 70)
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔐 Authentication:")
    print("   Login: POST http://localhost:8000/api/auth/login")
    print("   Default credentials: admin / admin123!")
    print("📡 WebSocket: ws://localhost:8000/api/ws")
    print("📊 Stats: http://localhost:8000/api/ws/stats")
    print("=" * 70 + "\n")

    # Start background task for simulated data
    asyncio.create_task(simulate_periodic_data())


if __name__ == "__main__":
    uvicorn.run(
        "full_test_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
    )
