"""
Pytest configuration and fixtures.

This file contains shared fixtures and configuration for all tests.
"""

import pytest
import responses

from src.unifi_client import UniFiClient


@pytest.fixture(scope="session")
def api_key():
    """Return a test API key."""
    return "test-api-key-12345"


@pytest.fixture(scope="session")
def base_url():
    """Return the test base URL."""
    return "https://api.ui.com/v1"


@pytest.fixture
def client(api_key, base_url):
    """Create a UniFi client instance for testing."""
    return UniFiClient(api_key, base_url)


@pytest.fixture
def mock_responses():
    """Enable responses mock for HTTP requests."""
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture
def sample_host():
    """Return a sample host data structure."""
    return {
        "id": "test-host-id-123",
        "hardwareId": "hw-id-456",
        "type": "console",
        "ipAddress": "192.168.1.100",
        "owner": True,
        "isBlocked": False,
        "registrationTime": "2020-08-23T18:34:03Z",
        "lastConnectionStateChange": "2025-10-14T18:25:22Z",
        "latestBackupTime": "2025-10-14T07:31:53Z",
    }


@pytest.fixture
def sample_hosts_list(sample_host):
    """Return a list of sample hosts."""
    return [
        sample_host,
        {
            "id": "test-host-id-456",
            "type": "device",
            "ipAddress": "192.168.1.101",
            "owner": False,
            "isBlocked": False,
        },
    ]
