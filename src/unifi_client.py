"""
UniFi API Client

This module provides a simple client for interacting with the UniFi Site Manager API.
"""

import logging
from typing import Any, Dict, List, Optional

import requests

from src.exceptions import (
    UniFiAPIError,
    UniFiAuthError,
    UniFiConnectionError,
    UniFiNotFoundError,
    UniFiRateLimitError,
    UniFiServerError,
    UniFiTimeoutError,
)
from src.retry import get_retry_delay, retry_with_backoff, should_retry


class UniFiClient:
    """Client for interacting with the UniFi Site Manager API."""

    def __init__(self, api_key: str, base_url: str = "https://api.ui.com/v1"):
        """
        Initialize the UniFi API client.

        Args:
            api_key: Your UniFi API key
            base_url: Base URL for the API (default: https://api.ui.com/v1)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(
            {"X-API-KEY": self.api_key, "Content-Type": "application/json"}
        )

        # Set up logging
        self.logger = logging.getLogger(__name__)

    @retry_with_backoff(max_retries=3, base_delay=1.0)
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make an API request with automatic retry on transient failures.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            **kwargs: Additional arguments to pass to requests

        Returns:
            Response data as dictionary

        Raises:
            UniFiAuthError: Authentication failed (401, 403)
            UniFiNotFoundError: Resource not found (404)
            UniFiRateLimitError: Rate limit exceeded (429)
            UniFiServerError: Server error (5xx)
            UniFiConnectionError: Network/connection issues
            UniFiTimeoutError: Request timeout
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        self.logger.debug(f"Making {method} request to {url}")

        try:
            response = self.session.request(method, url, **kwargs)

            # Check for specific error status codes
            if response.status_code == 401:
                raise UniFiAuthError(
                    "Authentication failed. Check your API key.", response=response
                )

            if response.status_code == 403:
                raise UniFiAuthError(
                    "Access forbidden. API key may lack permissions.", response=response
                )

            if response.status_code == 404:
                raise UniFiNotFoundError(
                    f"Resource not found: {endpoint}", response=response
                )

            if response.status_code == 429:
                retry_after = get_retry_delay(response)
                raise UniFiRateLimitError(
                    "Rate limit exceeded. Slow down requests.",
                    response=response,
                    retry_after=retry_after,
                )

            if 500 <= response.status_code < 600:
                raise UniFiServerError(
                    f"Server error ({response.status_code}). " "Try again later.",
                    response=response,
                )

            # Raise for any other error status
            response.raise_for_status()

            # Return JSON if available, otherwise return empty dict
            if response.content:
                return response.json()
            return {}

        except requests.exceptions.Timeout as e:
            self.logger.error(f"Request timeout: {e}")
            raise UniFiTimeoutError(
                f"Request to {endpoint} timed out", response=None
            ) from e

        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Connection error: {e}")
            raise UniFiConnectionError(
                f"Failed to connect to {self.base_url}", response=None
            ) from e

        except requests.exceptions.RequestException as e:
            # Catch any other requests exceptions
            self.logger.error(f"Request error: {e}")
            raise UniFiAPIError(
                f"Request failed: {str(e)}", response=getattr(e, "response", None)
            ) from e

    def get_hosts(self) -> List[Dict[str, Any]]:
        """
        Get a list of all hosts/devices in the network.

        Returns:
            List of host information dictionaries
        """
        self.logger.info("Fetching list of hosts")
        response = self._make_request("GET", "/hosts")

        # The response structure may vary; adjust based on actual API response
        if isinstance(response, list):
            return response
        elif isinstance(response, dict) and "data" in response:
            return response["data"]
        return []

    def get_host(self, host_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific host.

        Args:
            host_id: The ID of the host

        Returns:
            Host information dictionary
        """
        self.logger.info(f"Fetching information for host {host_id}")
        return self._make_request("GET", f"/hosts/{host_id}")

    def get_host_status(self, host_id: str) -> Dict[str, Any]:
        """
        Get the current status of a specific host.

        Args:
            host_id: The ID of the host

        Returns:
            Host status information
        """
        self.logger.info(f"Fetching status for host {host_id}")
        return self._make_request("GET", f"/hosts/{host_id}/status")

    def reboot_host(self, host_id: str) -> Dict[str, Any]:
        """
        Reboot a specific host/device.

        Args:
            host_id: The ID of the host to reboot

        Returns:
            Response from the API
        """
        self.logger.warning(f"Rebooting host {host_id}")
        return self._make_request("POST", f"/hosts/{host_id}/reboot")

    def test_connection(self) -> bool:
        """
        Test if the API connection is working.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            self.get_hosts()
            self.logger.info("API connection test successful")
            return True
        except Exception as e:
            self.logger.error(f"API connection test failed: {e}")
            return False


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """
    Set up logging configuration.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
    """
    logging_config = {
        "level": getattr(logging, log_level.upper()),
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "datefmt": "%Y-%m-%d %H:%M:%S",
    }

    if log_file:
        import os

        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        logging_config["filename"] = log_file

    logging.basicConfig(**logging_config)
