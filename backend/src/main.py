"""Main FastAPI application."""

import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.src.api import (
    alerts,
    analytics,
    auth,
    channels,
    devices,
    health,
    rules,
    websocket,
)
from backend.src.config import get_settings
from backend.src.middleware.error_handler import add_exception_handlers

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handlers
add_exception_handlers(app)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(devices.router, prefix="/api/devices", tags=["Devices"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(rules.router, prefix="/api/rules", tags=["Rules"])
app.include_router(channels.router, prefix="/api/channels", tags=["Channels"])
app.include_router(
    analytics.router, prefix="/api/analytics", tags=["Analytics"]
)
app.include_router(websocket.router, tags=["WebSocket"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "docs": "/docs",
        "health": "/health",
        "websocket": "/ws",
    }


@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("FastAPI application starting up")
    logger.info(f"WebSocket endpoint available at: ws://localhost:8000/ws")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
    )
