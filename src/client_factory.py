"""
UniFi Client Factory

Provides factory function to get the appropriate UniFi client based on config
"""

from typing import Union

from config import (
    API_KEY,
    API_TYPE,
    BASE_URL,
    CONTROLLER_HOST,
    CONTROLLER_PASSWORD,
    CONTROLLER_PORT,
    CONTROLLER_SITE,
    CONTROLLER_USERNAME,
    CONTROLLER_VERIFY_SSL,
)
from src.unifi_client import UniFiClient
from src.unifi_controller import UniFiController


def get_unifi_client() -> Union[UniFiClient, UniFiController]:
    """
    Get the appropriate UniFi client based on configuration.

    Returns:
        UniFiClient for cloud API or UniFiController for local controller

    Example:
        ```python
        client = get_unifi_client()

        # Works with either client type
        if isinstance(client, UniFiController):
            client.login()

        devices = client.get_devices()
        ```
    """
    api_type = getattr(API_TYPE, "API_TYPE", "cloud").lower()

    if api_type == "local":
        # Use local controller
        return UniFiController(
            host=CONTROLLER_HOST,
            username=CONTROLLER_USERNAME,
            password=CONTROLLER_PASSWORD,
            port=CONTROLLER_PORT,
            site=CONTROLLER_SITE,
            verify_ssl=CONTROLLER_VERIFY_SSL,
        )
    else:
        # Use cloud Site Manager API
        return UniFiClient(api_key=API_KEY, base_url=BASE_URL)
