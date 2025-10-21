"""
Wrapper script to run the FastAPI app with correct sys.path.
This ensures sys.path is set before uvicorn spawns subprocesses.
"""

import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import uvicorn

if __name__ == "__main__":
    # Use import string for reload to work properly
    uvicorn.run(
        "backend.src.main:app",  # Import string enables reload
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[str(project_root)],
    )
