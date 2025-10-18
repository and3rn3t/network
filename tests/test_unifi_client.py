"""
Unit tests for the UniFiClient class.

Tests cover basic functionality, error handling, and retry logic.
"""

from unittest.mock import MagicMock, patch

import pytest
import responses

from src.exceptions import (
    UniFiAuthError,
    UniFiConnectionError,
    UniFiNotFoundError,
    UniFiRateLimitError,
    UniFiServerError,
    UniFiTimeoutError,
)
from src.unifi_client import UniFiClient


class TestUniFiClientInitialization:
    """Test UniFiClient initialization."""

    def test_client_initialization(self, api_key, base_url):
        """Test that client initializes correctly."""
        client = UniFiClient(api_key, base_url)

        assert client.api_key == api_key
        assert client.base_url == base_url
        assert "X-API-KEY" in client.session.headers
        assert client.session.headers["X-API-KEY"] == api_key
        assert client.session.headers["Content-Type"] == "application/json"

    def test_client_strips_trailing_slash(self, api_key):
        """Test that trailing slash is removed from base URL."""
        client = UniFiClient(api_key, "https://api.ui.com/v1/")
        assert client.base_url == "https://api.ui.com/v1"


class TestGetHosts:
    """Test get_hosts method."""

    @responses.activate
    def test_get_hosts_success(self, client, base_url, sample_hosts_list):
        """Test successful hosts retrieval."""
        responses.add(
            responses.GET, f"{base_url}/hosts", json=sample_hosts_list, status=200
        )

        hosts = client.get_hosts()

        assert len(hosts) == 2
        assert hosts[0]["id"] == "test-host-id-123"
        assert hosts[1]["id"] == "test-host-id-456"

    @responses.activate
    def test_get_hosts_with_data_wrapper(self, client, base_url, sample_hosts_list):
        """Test hosts retrieval when response is wrapped in data object."""
        responses.add(
            responses.GET,
            f"{base_url}/hosts",
            json={"data": sample_hosts_list},
            status=200,
        )

        hosts = client.get_hosts()

        assert len(hosts) == 2
        assert hosts[0]["id"] == "test-host-id-123"

    @responses.activate
    def test_get_hosts_empty_list(self, client, base_url):
        """Test hosts retrieval when no hosts exist."""
        responses.add(responses.GET, f"{base_url}/hosts", json=[], status=200)

        hosts = client.get_hosts()

        assert hosts == []

    @responses.activate
    def test_get_hosts_auth_error(self, client, base_url):
        """Test hosts retrieval with authentication error."""
        responses.add(
            responses.GET,
            f"{base_url}/hosts",
            json={"error": "Unauthorized"},
            status=401,
        )

        with pytest.raises(UniFiAuthError) as exc_info:
            client.get_hosts()

        assert "Authentication failed" in str(exc_info.value)


class TestGetHost:
    """Test get_host method."""

    @responses.activate
    def test_get_host_success(self, client, base_url, sample_host):
        """Test successful single host retrieval."""
        host_id = sample_host["id"]
        responses.add(
            responses.GET, f"{base_url}/hosts/{host_id}", json=sample_host, status=200
        )

        host = client.get_host(host_id)

        assert host["id"] == host_id
        assert host["type"] == "console"
        assert host["ipAddress"] == "192.168.1.100"

    @responses.activate
    def test_get_host_not_found(self, client, base_url):
        """Test host retrieval with non-existent ID."""
        responses.add(
            responses.GET,
            f"{base_url}/hosts/invalid-id",
            json={"error": "Not found"},
            status=404,
        )

        with pytest.raises(UniFiNotFoundError) as exc_info:
            client.get_host("invalid-id")

        assert "not found" in str(exc_info.value).lower()


class TestGetHostStatus:
    """Test get_host_status method."""

    @responses.activate
    def test_get_host_status_success(self, client, base_url):
        """Test successful host status retrieval."""
        host_id = "test-host-123"
        status_data = {
            "id": host_id,
            "state": "online",
            "uptime": 86400,
            "last_seen": "2025-10-17T18:00:00Z",
        }

        responses.add(
            responses.GET,
            f"{base_url}/hosts/{host_id}/status",
            json=status_data,
            status=200,
        )

        status = client.get_host_status(host_id)

        assert status["state"] == "online"
        assert status["uptime"] == 86400


class TestRebootHost:
    """Test reboot_host method."""

    @responses.activate
    def test_reboot_host_success(self, client, base_url):
        """Test successful host reboot."""
        host_id = "test-host-123"
        responses.add(
            responses.POST,
            f"{base_url}/hosts/{host_id}/reboot",
            json={"status": "success", "message": "Reboot command sent"},
            status=200,
        )

        result = client.reboot_host(host_id)

        assert result["status"] == "success"

    @responses.activate
    def test_reboot_host_forbidden(self, client, base_url):
        """Test host reboot with insufficient permissions."""
        host_id = "test-host-123"
        responses.add(
            responses.POST,
            f"{base_url}/hosts/{host_id}/reboot",
            json={"error": "Forbidden"},
            status=403,
        )

        with pytest.raises(UniFiAuthError):
            client.reboot_host(host_id)


class TestErrorHandling:
    """Test error handling and custom exceptions."""

    @responses.activate
    def test_rate_limit_error(self, client, base_url):
        """Test rate limit error handling."""
        responses.add(
            responses.GET,
            f"{base_url}/hosts",
            json={"error": "Rate limit exceeded"},
            status=429,
            headers={"Retry-After": "60"},
        )

        with pytest.raises(UniFiRateLimitError) as exc_info:
            client.get_hosts()

        assert exc_info.value.retry_after == 60.0

    @responses.activate
    def test_server_error(self, client, base_url):
        """Test server error handling."""
        responses.add(
            responses.GET,
            f"{base_url}/hosts",
            json={"error": "Internal server error"},
            status=500,
        )

        with pytest.raises(UniFiServerError):
            client.get_hosts()

    @responses.activate
    def test_connection_error(self, client):
        """Test connection error handling."""
        with patch.object(client.session, "request") as mock_request:
            mock_request.side_effect = Exception("Connection refused")

            with pytest.raises(Exception):
                client.get_hosts()

    @responses.activate
    def test_timeout_error(self, client):
        """Test timeout error handling."""
        import requests as req

        with patch.object(client.session, "request") as mock_request:
            mock_request.side_effect = req.exceptions.Timeout("Request timeout")

            with pytest.raises(UniFiTimeoutError):
                client.get_hosts()


class TestRetryLogic:
    """Test retry logic with exponential backoff."""

    @responses.activate
    def test_retry_on_rate_limit(self, client, base_url, sample_hosts_list):
        """Test that requests retry on rate limit errors."""
        # First request fails with 429, second succeeds
        responses.add(
            responses.GET, f"{base_url}/hosts", json={"error": "Rate limit"}, status=429
        )
        responses.add(
            responses.GET, f"{base_url}/hosts", json=sample_hosts_list, status=200
        )

        hosts = client.get_hosts()

        assert len(hosts) == 2
        assert len(responses.calls) == 2  # Should have made 2 requests

    @responses.activate
    def test_retry_on_server_error(self, client, base_url, sample_hosts_list):
        """Test that requests retry on server errors."""
        # First request fails with 500, second succeeds
        responses.add(
            responses.GET,
            f"{base_url}/hosts",
            json={"error": "Server error"},
            status=500,
        )
        responses.add(
            responses.GET, f"{base_url}/hosts", json=sample_hosts_list, status=200
        )

        hosts = client.get_hosts()

        assert len(hosts) == 2
        assert len(responses.calls) == 2


class TestTestConnection:
    """Test test_connection method."""

    @responses.activate
    def test_connection_successful(self, client, base_url):
        """Test successful connection test."""
        responses.add(responses.GET, f"{base_url}/hosts", json=[], status=200)

        result = client.test_connection()

        assert result is True

    @responses.activate
    def test_connection_failed(self, client, base_url):
        """Test failed connection test."""
        responses.add(
            responses.GET,
            f"{base_url}/hosts",
            json={"error": "Unauthorized"},
            status=401,
        )

        result = client.test_connection()

        assert result is False
