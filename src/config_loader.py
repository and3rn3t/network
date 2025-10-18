"""
Configuration loader utility.

Supports loading from config.py or .env file.
"""

import os
from pathlib import Path
from typing import Optional


def load_api_key() -> Optional[str]:
    """
    Load API key from config.py or .env file.

    Priority:
    1. Environment variable UNIFI_API_KEY
    2. config.py file
    3. .env file

    Returns:
        API key string or None if not found
    """
    # Try environment variable first
    api_key = os.getenv("UNIFI_API_KEY")
    if api_key:
        return api_key

    # Try config.py
    try:
        import config

        if hasattr(config, "API_KEY"):
            return config.API_KEY
    except ImportError:
        pass

    # Try .env file
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        api_key = _load_from_env_file(env_file)
        if api_key:
            return api_key

    return None


def _load_from_env_file(env_file: Path) -> Optional[str]:
    """Load API key from .env file."""
    with open(env_file, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("UNIFI_API_KEY="):
                return line.split("=", 1)[1].strip()
    return None


def get_base_url() -> str:
    """
    Get the base URL for the API.

    Returns:
        Base URL string
    """
    # Try environment variable
    base_url = os.getenv("UNIFI_BASE_URL")
    if base_url:
        return base_url

    # Try config.py
    try:
        import config

        if hasattr(config, "BASE_URL"):
            return config.BASE_URL
    except ImportError:
        pass

    # Default
    return "https://api.ui.com/v1"
