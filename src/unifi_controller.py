"""
UniFi Network Controller Client

This module provides a client for interacting with a local UniFi Network Controller.
This is different from the UniFi Site Manager API - this connects directly to
your on-premise or cloud-hosted UniFi Network Application.

API Documentation: https://ubntwiki.com/products/software/unifi-controller/api
"""

import logging
import re
import time
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

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


def validate_mac_address(mac: str) -> bool:
    """
    Validate MAC address format.

    Args:
        mac: MAC address string

    Returns:
        True if valid MAC address format

    Supports formats:
        - xx:xx:xx:xx:xx:xx
        - xx-xx-xx-xx-xx-xx
        - xxxxxxxxxxxx
    """
    if not mac:
        return False

    # Remove separators
    clean_mac = mac.replace(":", "").replace("-", "").replace(".", "")

    # Should be exactly 12 hex characters
    if len(clean_mac) != 12:
        return False

    try:
        int(clean_mac, 16)
        return True
    except ValueError:
        return False


def normalize_mac_address(mac: str) -> str:
    """
    Normalize MAC address to lowercase without separators.

    Args:
        mac: MAC address in any format

    Returns:
        Normalized MAC (lowercase, no separators)

    Example:
        >>> normalize_mac_address("AA:BB:CC:DD:EE:FF")
        'aabbccddeeff'
    """
    return mac.replace(":", "").replace("-", "").replace(".", "").lower()


def retry_on_network_error(max_retries: int = 3, backoff_factor: float = 2.0):
    """
    Decorator to retry function on network errors with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Multiplier for delay between retries

    Example:
        @retry_on_network_error(max_retries=3)
        def my_api_call():
            # ... network call ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (
                    UniFiConnectionError,
                    UniFiTimeoutError,
                    UniFiServerError,
                ) as e:
                    last_exception = e
                    if attempt < max_retries:
                        delay = backoff_factor**attempt
                        logging.getLogger(__name__).warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed: {e}. "
                            f"Retrying in {delay:.1f}s..."
                        )
                        time.sleep(delay)
                    else:
                        logging.getLogger(__name__).error(
                            f"All {max_retries + 1} attempts failed"
                        )
                        raise last_exception

            # Should never reach here, but just in case
            if last_exception:
                raise last_exception

        return wrapper

    return decorator


class UniFiController:
    """
    Client for interacting with UniFi Network Controller (local/on-premise).

    This client handles authentication, session management, and provides
    methods for device and client management operations.

    Example:
        ```python
        controller = UniFiController(
            host="192.168.1.1",
            username="admin",
            password="password",
            site="default"
        )
        controller.login()

        # Get all devices
        devices = controller.get_devices()

        # Reboot a device
        controller.reboot_device(device_mac)
        ```
    """

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        port: int = 443,
        site: str = "default",
        verify_ssl: bool = True,
        timeout: int = 30,
    ):
        """
        Initialize UniFi Controller client.

        Args:
            host: Controller hostname or IP address
            username: Admin username
            password: Admin password
            port: Controller port (default: 443)
            site: Site name (default: "default")
            verify_ssl: Verify SSL certificates (default: True)
            timeout: Request timeout in seconds (default: 30)
        """
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.site = site
        self.verify_ssl = verify_ssl
        self.timeout = timeout

        # Build base URL
        self.base_url = f"https://{host}:{port}"

        # Session management
        self.session = requests.Session()
        self.session.verify = verify_ssl
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

        # Logging
        self.logger = logging.getLogger(__name__)

        # Track login state and controller type
        self._logged_in = False
        self._is_udm = None  # Auto-detect UDM vs standard controller

    def login(self) -> bool:
        """
        Authenticate with the UniFi controller.

        Returns:
            True if login successful

        Raises:
            UniFiAuthError: If authentication fails
        """
        # Skip if already logged in
        if self._logged_in:
            return True

        # Try /api/auth/login first (UDM/UDM-Pro), fallback to /api/login
        endpoints = ["/api/auth/login", "/api/login"]
        payload = {"username": self.username, "password": self.password}

        for endpoint in endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                self.logger.info(f"Logging in to {self.host} via {endpoint}")

                response = self.session.post(
                    url, json=payload, timeout=self.timeout, verify=self.verify_ssl
                )

                if response.status_code == 200:
                    self._logged_in = True
                    # Detect if this is a UDM (uses /api/auth/login)
                    self._is_udm = endpoint == "/api/auth/login"
                    self.logger.info(f"Login successful via {endpoint}")
                    return True
                elif response.status_code == 401:
                    # Try next endpoint
                    self.logger.debug(f"Login failed at {endpoint}, trying next")
                    continue
                elif response.status_code == 400:
                    raise UniFiAuthError(
                        "Invalid credentials. Check username and password.",
                        response=response,
                    )
                else:
                    # Try next endpoint for other errors too
                    continue

            except requests.exceptions.Timeout:
                raise UniFiTimeoutError(
                    f"Connection to {self.host} timed out", response=None
                )
            except requests.exceptions.ConnectionError as e:
                raise UniFiConnectionError(
                    f"Could not connect to {self.host}:{self.port}", response=None
                ) from e

        # If we get here, all endpoints failed
        raise UniFiAuthError(
            f"Login failed with all endpoints. Check credentials.",
            response=None,
        )

    def logout(self) -> bool:
        """
        Logout from the UniFi controller.

        Returns:
            True if logout successful
        """
        if not self._logged_in:
            return True

        # Try both logout endpoints (UDM uses /api/auth/logout)
        endpoints = ["/api/auth/logout", "/api/logout"]

        for endpoint in endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                response = self.session.post(url, timeout=self.timeout)

                if response.status_code == 200:
                    self._logged_in = False
                    self.logger.info(f"Logout successful via {endpoint}")
                    return True

            except Exception as e:
                self.logger.debug(f"Logout failed at {endpoint}: {e}")
                continue

        self.logger.warning("Logout failed at all endpoints")
        return False

    def _ensure_logged_in(self):
        """Ensure we're logged in before making API calls."""
        if not self._logged_in:
            self.login()

    def _make_request(
        self, method: str, endpoint: str, data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make an API request to the controller.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (e.g., /api/s/default/stat/device)
            data: Request payload (for POST/PUT)

        Returns:
            Response data dictionary

        Raises:
            UniFiAuthError: Authentication required or failed
            UniFiNotFoundError: Resource not found (404)
            UniFiServerError: Server error (5xx)
            UniFiRateLimitError: Rate limit exceeded
            UniFiTimeoutError: Request timed out
            UniFiConnectionError: Network connection failed
        """
        self._ensure_logged_in()

        # Build correct endpoint for UDM vs standard controller
        endpoint = self._build_endpoint(endpoint)
        url = f"{self.base_url}{endpoint}"
        self.logger.debug(f"{method} {url}")

        try:
            if method == "GET":
                response = self.session.get(url, timeout=self.timeout)
            elif method == "POST":
                response = self.session.post(url, json=data, timeout=self.timeout)
            elif method == "PUT":
                response = self.session.put(url, json=data, timeout=self.timeout)
            elif method == "DELETE":
                response = self.session.delete(url, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            # Handle specific HTTP errors
            if response.status_code == 401:
                self._logged_in = False
                error_msg = "Authentication required. Session may have expired."
                try:
                    error_data = response.json()
                    if "meta" in error_data and "msg" in error_data["meta"]:
                        error_msg = f"{error_msg} ({error_data['meta']['msg']})"
                except Exception:
                    pass
                raise UniFiAuthError(error_msg, response=response)

            elif response.status_code == 403:
                error_msg = (
                    "Permission denied. User may not have access to this resource."
                )
                try:
                    error_data = response.json()
                    if "meta" in error_data and "msg" in error_data["meta"]:
                        error_msg = error_data["meta"]["msg"]
                except Exception:
                    pass
                raise UniFiAuthError(error_msg, response=response)

            elif response.status_code == 404:
                error_msg = f"Resource not found: {endpoint}"
                try:
                    error_data = response.json()
                    if "meta" in error_data and "msg" in error_data["meta"]:
                        error_msg = error_data["meta"]["msg"]
                except Exception:
                    pass
                raise UniFiNotFoundError(error_msg, response=response)

            elif response.status_code == 429:
                # Rate limiting
                retry_after = response.headers.get("Retry-After")
                retry_seconds = int(retry_after) if retry_after else 60
                raise UniFiRateLimitError(
                    f"Rate limit exceeded. Retry after {retry_seconds} seconds.",
                    response=response,
                    retry_after=retry_seconds,
                )

            elif 500 <= response.status_code < 600:
                error_msg = f"Server error ({response.status_code})"
                try:
                    error_data = response.json()
                    if "meta" in error_data and "msg" in error_data["meta"]:
                        error_msg = f"{error_msg}: {error_data['meta']['msg']}"
                except Exception:
                    pass
                raise UniFiServerError(error_msg, response=response)

            # Check for other error codes
            if response.status_code >= 400:
                error_msg = f"Request failed with status {response.status_code}"
                try:
                    error_data = response.json()
                    if "meta" in error_data and "msg" in error_data["meta"]:
                        error_msg = error_data["meta"]["msg"]
                except Exception:
                    pass
                raise UniFiAPIError(error_msg, response=response)

            # Parse JSON response
            if response.content:
                result = response.json()

                # UniFi API returns data in {"meta": {...}, "data": [...]} format
                if isinstance(result, dict) and "data" in result:
                    return result["data"]
                return result

            return {}

        except requests.exceptions.Timeout as e:
            raise UniFiTimeoutError(
                f"Request to {endpoint} timed out after {self.timeout}s", response=None
            ) from e
        except requests.exceptions.ConnectionError as e:
            raise UniFiConnectionError(
                f"Failed to connect to {self.host}:{self.port}. "
                f"Check if controller is reachable: {str(e)}",
                response=None,
            ) from e
        except (
            UniFiAPIError,
            UniFiAuthError,
            UniFiNotFoundError,
            UniFiServerError,
            UniFiRateLimitError,
            UniFiTimeoutError,
            UniFiConnectionError,
        ):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Catch any other unexpected errors
            self.logger.error(f"Unexpected error in request: {e}")
            raise UniFiAPIError(f"Unexpected error: {str(e)}", response=None) from e

    # =============================================================================
    # Device Management Methods
    # =============================================================================

    @retry_on_network_error(max_retries=3)
    def get_devices(self) -> List[Dict[str, Any]]:
        """
        Get list of all devices on the network.

        Returns:
            List of device dictionaries

        Example:
            ```python
            devices = controller.get_devices()
            for device in devices:
                print(f"{device['name']} - {device['ip']} - {device['state']}")
            ```
        """
        endpoint = f"/api/s/{self.site}/stat/device"
        result = self._make_request("GET", endpoint)
        # Ensure we return a list
        if isinstance(result, list):
            return result
        return []

    def get_device(self, mac: str) -> Dict[str, Any]:
        """
        Get details for a specific device by MAC address.

        Args:
            mac: Device MAC address (format: xx:xx:xx:xx:xx:xx or xxxxxxxxxx)

        Returns:
            Device information dictionary

        Raises:
            UniFiNotFoundError: If device not found
        """
        mac = self._normalize_mac(mac)
        devices = self.get_devices()

        for device in devices:
            if self._normalize_mac(device.get("mac", "")) == mac:
                return device

        raise UniFiNotFoundError(f"Device with MAC {mac} not found", response=None)

    def reboot_device(self, mac: str) -> Dict[str, Any]:
        """
        Reboot a device.

        Args:
            mac: Device MAC address

        Returns:
            API response

        Example:
            ```python
            result = controller.reboot_device("aa:bb:cc:dd:ee:ff")
            ```
        """
        mac = self._normalize_mac(mac)
        endpoint = f"/api/s/{self.site}/cmd/devmgr"
        payload = {"cmd": "restart", "mac": mac}

        return self._make_request("POST", endpoint, data=payload)

    def restart_device(self, mac: str) -> Dict[str, Any]:
        """
        Soft restart a device (restart services, not full reboot).

        Args:
            mac: Device MAC address

        Returns:
            API response
        """
        mac = self._normalize_mac(mac)
        endpoint = f"/api/s/{self.site}/cmd/devmgr"
        payload = {"cmd": "restart", "mac": mac, "reboot_type": "soft"}

        return self._make_request("POST", endpoint, data=payload)

    def locate_device(self, mac: str, enable: bool = True) -> Dict[str, Any]:
        """
        Enable/disable LED locate on a device.

        Args:
            mac: Device MAC address
            enable: True to turn on LED, False to turn off

        Returns:
            API response

        Example:
            ```python
            # Turn on locate LED
            controller.locate_device("aa:bb:cc:dd:ee:ff", True)

            # Wait for user to find device...
            time.sleep(30)

            # Turn off locate LED
            controller.locate_device("aa:bb:cc:dd:ee:ff", False)
            ```
        """
        mac = self._normalize_mac(mac)
        endpoint = f"/api/s/{self.site}/cmd/devmgr"
        payload = {"cmd": "set-locate", "mac": mac}

        return self._make_request("POST", endpoint, data=payload)

    def rename_device(self, mac: str, name: str) -> Dict[str, Any]:
        """
        Rename a device.

        Args:
            mac: Device MAC address
            name: New device name

        Returns:
            API response

        Example:
            ```python
            controller.rename_device("aa:bb:cc:dd:ee:ff", "Office Switch")
            ```
        """
        mac = self._normalize_mac(mac)
        device = self.get_device(mac)
        device_id = device.get("_id")

        if not device_id:
            raise UniFiAPIError(f"Could not get device ID for MAC {mac}")

        endpoint = f"/api/s/{self.site}/rest/device/{device_id}"
        payload = {"name": name}

        return self._make_request("PUT", endpoint, data=payload)

    def get_device_statistics(self, mac: str) -> Dict[str, Any]:
        """
        Get detailed statistics for a device.

        Args:
            mac: Device MAC address

        Returns:
            Device statistics including ports, CPU, memory, etc.
        """
        device = self.get_device(mac)
        return {
            "mac": device.get("mac"),
            "name": device.get("name"),
            "model": device.get("model"),
            "version": device.get("version"),
            "uptime": device.get("uptime", 0),
            "cpu": device.get("system-stats", {}).get("cpu", 0),
            "mem": device.get("system-stats", {}).get("mem", 0),
            "uplink": device.get("uplink", {}),
            "port_table": device.get("port_table", []),
            "temperatures": device.get("temperatures", []),
        }

    # =============================================================================
    # Client Management Methods
    # =============================================================================

    @retry_on_network_error(max_retries=3)
    def get_clients(self) -> List[Dict[str, Any]]:
        """
        Get list of all active clients.

        Returns:
            List of client dictionaries

        Example:
            ```python
            clients = controller.get_clients()
            for client in clients:
                print(f"{client['hostname']} - {client['ip']}")
            ```
        """
        endpoint = f"/api/s/{self.site}/stat/sta"
        result = self._make_request("GET", endpoint)
        # Ensure we return a list
        if isinstance(result, list):
            return result
        return []

    def get_client(self, mac: str) -> Dict[str, Any]:
        """
        Get details for a specific client by MAC address.

        Args:
            mac: Client MAC address

        Returns:
            Client information dictionary

        Raises:
            UniFiNotFoundError: If client not found
        """
        mac = self._normalize_mac(mac)
        clients = self.get_clients()

        for client in clients:
            if self._normalize_mac(client.get("mac", "")) == mac:
                return client

        raise UniFiNotFoundError(f"Client with MAC {mac} not found", response=None)

    def block_client(self, mac: str, duration: Optional[int] = None) -> Dict[str, Any]:
        """
        Block a client from the network.

        Args:
            mac: Client MAC address
            duration: Block duration in seconds (None for permanent)

        Returns:
            API response

        Example:
            ```python
            # Permanent block
            controller.block_client("aa:bb:cc:dd:ee:ff")

            # Temporary block for 1 hour
            controller.block_client("aa:bb:cc:dd:ee:ff", duration=3600)
            ```
        """
        mac = self._normalize_mac(mac)
        endpoint = f"/api/s/{self.site}/cmd/stamgr"

        if duration:
            # Temporary block
            payload = {"cmd": "block-sta", "mac": mac, "duration": duration}
        else:
            # Permanent block
            payload = {"cmd": "block-sta", "mac": mac}

        return self._make_request("POST", endpoint, data=payload)

    def unblock_client(self, mac: str) -> Dict[str, Any]:
        """
        Unblock a previously blocked client.

        Args:
            mac: Client MAC address

        Returns:
            API response

        Example:
            ```python
            controller.unblock_client("aa:bb:cc:dd:ee:ff")
            ```
        """
        mac = self._normalize_mac(mac)
        endpoint = f"/api/s/{self.site}/cmd/stamgr"
        payload = {"cmd": "unblock-sta", "mac": mac}

        return self._make_request("POST", endpoint, data=payload)

    def reconnect_client(self, mac: str) -> Dict[str, Any]:
        """
        Force a client to reconnect (disconnect and force re-authentication).

        Args:
            mac: Client MAC address

        Returns:
            API response

        Example:
            ```python
            controller.reconnect_client("aa:bb:cc:dd:ee:ff")
            ```
        """
        mac = self._normalize_mac(mac)
        endpoint = f"/api/s/{self.site}/cmd/stamgr"
        payload = {"cmd": "kick-sta", "mac": mac}

        return self._make_request("POST", endpoint, data=payload)

    def set_client_bandwidth(
        self, mac: str, download_kbps: int, upload_kbps: int
    ) -> Dict[str, Any]:
        """
        Set bandwidth limits for a client.

        Args:
            mac: Client MAC address
            download_kbps: Download limit in Kbps (0 for unlimited)
            upload_kbps: Upload limit in Kbps (0 for unlimited)

        Returns:
            API response

        Example:
            ```python
            # Limit to 10 Mbps down / 2 Mbps up
            controller.set_client_bandwidth("aa:bb:cc:dd:ee:ff", 10000, 2000)
            ```
        """
        mac = self._normalize_mac(mac)

        # Get client to find user_id
        client = self.get_client(mac)
        user_id = client.get("_id")

        if not user_id:
            raise UniFiAPIError(f"Could not get user ID for client {mac}")

        endpoint = f"/api/s/{self.site}/rest/user/{user_id}"
        payload = {
            "qos_rate_max_down": download_kbps,
            "qos_rate_max_up": upload_kbps,
        }

        return self._make_request("PUT", endpoint, data=payload)

    def authorize_guest(self, mac: str, duration_seconds: int) -> Dict[str, Any]:
        """
        Authorize a guest for a limited time.

        Args:
            mac: Client MAC address
            duration_seconds: Authorization duration in seconds

        Returns:
            API response

        Example:
            ```python
            # Authorize for 24 hours
            controller.authorize_guest("aa:bb:cc:dd:ee:ff", 86400)
            ```
        """
        mac = self._normalize_mac(mac)
        endpoint = f"/api/s/{self.site}/cmd/stamgr"

        # Calculate expiration time (minutes from now)
        duration_minutes = duration_seconds // 60

        payload = {
            "cmd": "authorize-guest",
            "mac": mac,
            "minutes": duration_minutes,
        }

        return self._make_request("POST", endpoint, data=payload)

    def get_client_history(self, mac: str, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get connection history for a client.

        Args:
            mac: Client MAC address
            hours: Hours of history to retrieve (default: 24)

        Returns:
            List of client session records

        Note:
            Historical data availability depends on controller retention settings.
        """
        mac = self._normalize_mac(mac)

        # Calculate time range
        end_time = int(time.time() * 1000)  # milliseconds
        start_time = end_time - (hours * 3600 * 1000)

        endpoint = f"/api/s/{self.site}/stat/session"
        # Note: This endpoint may require additional query parameters
        # depending on your UniFi controller version

        try:
            sessions = self._make_request("GET", endpoint)
            # Filter sessions for this MAC
            return [
                session
                for session in sessions
                if self._normalize_mac(session.get("mac", "")) == mac
            ]
        except Exception as e:
            self.logger.warning(f"Could not retrieve client history: {e}")
            return []

    # =============================================================================
    # Site Management Methods
    # =============================================================================

    @retry_on_network_error(max_retries=3)
    def get_sites(self) -> List[Dict[str, Any]]:
        """
        Get list of all sites.

        Returns:
            List of site dictionaries

        Example:
            ```python
            sites = controller.get_sites()
            for site in sites:
                print(f"{site['desc']} ({site['name']})")
            ```
        """
        # Try UDM path first, fallback to standard
        endpoints = ["/proxy/network/api/self/sites", "/api/self/sites"]

        for endpoint in endpoints:
            try:
                result = self._make_request("GET", endpoint)
                # Ensure we return a list
                if isinstance(result, list):
                    return result
                return []
            except UniFiNotFoundError:
                # Try next endpoint
                continue

        # If all failed, raise the error
        raise UniFiNotFoundError("Could not find sites endpoint", response=None)

    # =============================================================================
    # Utility Methods
    # =============================================================================

    def _build_endpoint(self, path: str) -> str:
        """
        Build the correct API endpoint for UDM vs standard controller.

        Args:
            path: API path (e.g., "/api/s/{site}/stat/device")

        Returns:
            Full endpoint path with UDM proxy prefix if needed
        """
        if self._is_udm and path.startswith("/api/s/"):
            # UDM requires /proxy/network prefix for site-specific endpoints
            return f"/proxy/network{path}"
        return path

    @staticmethod
    def _normalize_mac(mac: str) -> str:
        """
        Normalize MAC address to lowercase without separators.

        Args:
            mac: MAC address in any format

        Returns:
            Normalized MAC (e.g., "aabbccddeeff")

        Raises:
            ValueError: If MAC address format is invalid
        """
        if not mac:
            raise ValueError("MAC address cannot be empty")

        # Remove common separators
        clean_mac = mac.replace(":", "").replace("-", "").replace(".", "").strip()

        # Validate format
        if len(clean_mac) != 12:
            raise ValueError(
                f"Invalid MAC address format: {mac}. "
                f"Expected 12 hex characters, got {len(clean_mac)}"
            )

        try:
            int(clean_mac, 16)
        except ValueError as e:
            raise ValueError(
                f"Invalid MAC address format: {mac}. "
                f"Must contain only hexadecimal characters (0-9, A-F)"
            ) from e

        return clean_mac.lower()

    def test_connection(self) -> bool:
        """
        Test if connection to controller is working.

        Returns:
            True if connection successful

        Example:
            ```python
            if controller.test_connection():
                print("Connected!")
            else:
                print("Connection failed")
            ```
        """
        try:
            self.login()
            self.get_sites()
            return True
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False

    def __enter__(self):
        """Context manager entry - login."""
        self.login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - logout."""
        self.logout()
