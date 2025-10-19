"""Minimal authentication test server."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.src.api import auth

# Create minimal FastAPI app
app = FastAPI(title="Auth Test Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include auth router
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Auth test server running", "status": "ok"}


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 STARTING AUTH TEST SERVER")
    print("=" * 60)
    print("📍 URL: http://127.0.0.1:8888")
    print("🔐 Default credentials: admin / admin123!")
    print("=" * 60 + "\n")

    uvicorn.run(app, host="127.0.0.1", port=8888, log_level="info")
