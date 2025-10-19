"""Health check endpoint."""

from datetime import datetime

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "0.1.0",
    }


@router.get("/api/health")
async def api_health_check():
    """API health check endpoint."""
    return {
        "status": "healthy",
        "api": "operational",
        "timestamp": datetime.now().isoformat(),
    }
