"""Minimal test server for WebSocket functionality."""

import asyncio
import random
import sys
from datetime import datetime
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.src.api.websocket import router as websocket_router
from backend.src.services.websocket_manager import manager

# Create FastAPI app
app = FastAPI(
    title="UniFi Network API - WebSocket Test",
    version="0.1.0",
    description="Test server for WebSocket functionality",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include WebSocket router
app.include_router(websocket_router, prefix="/api", tags=["websocket"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "UniFi Network WebSocket Test Server",
        "websocket": "/ws",
        "stats": "/api/ws/stats",
        "test_client": "Open websocket_test.html in your browser",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


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
            print(
                f"📊 Broadcasted metrics to {len(manager.rooms.get('metrics', []))} clients"
            )

        except Exception as e:
            print(f"Error broadcasting metrics: {e}")

        await asyncio.sleep(10)  # Broadcast every 10 seconds


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    print("\n" + "=" * 70)
    print("🚀 UniFi Network WebSocket Test Server Starting...")
    print("=" * 70)
    print(f"📡 WebSocket endpoint: ws://localhost:8000/ws")
    print(f"📊 Stats endpoint: http://localhost:8000/api/ws/stats")
    print(f"🌐 Test client: Open backend/websocket_test.html in your browser")
    print(f"📝 API docs: http://localhost:8000/docs")
    print("=" * 70 + "\n")

    # Start background task for simulated data
    asyncio.create_task(simulate_periodic_data())


if __name__ == "__main__":
    uvicorn.run(
        "test_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
    )
