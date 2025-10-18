"""
Unit tests for custom exceptions.

Tests ensure exceptions are raised correctly and contain proper information.
"""

import pytest

from src.exceptions import (
    UniFiAPIError,
    UniFiAuthError,
    UniFiConnectionError,
    UniFiNotFoundError,
    UniFiRateLimitError,
    UniFiServerError,
    UniFiTimeoutError,
    UniFiValidationError,
)


class TestUniFiAPIError:
    """Test base UniFiAPIError exception."""

    def test_basic_error(self):
        """Test basic error creation."""
        error = UniFiAPIError("Test error")

        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.response is None
        assert error.status_code is None

    def test_error_with_response(self):
        """Test error with response object."""
        from unittest.mock import Mock

        mock_response = Mock()
        mock_response.status_code = 400

        error = UniFiAPIError("Test error", response=mock_response)

        assert error.status_code == 400
        assert error.response == mock_response


class TestUniFiAuthError:
    """Test UniFiAuthError exception."""

    def test_auth_error_inherits_from_base(self):
        """Test that UniFiAuthError inherits from UniFiAPIError."""
        error = UniFiAuthError("Auth failed")

        assert isinstance(error, UniFiAPIError)
        assert isinstance(error, UniFiAuthError)

    def test_auth_error_message(self):
        """Test auth error message."""
        error = UniFiAuthError("Invalid API key")

        assert "Invalid API key" in str(error)


class TestUniFiRateLimitError:
    """Test UniFiRateLimitError exception."""

    def test_rate_limit_error_basic(self):
        """Test basic rate limit error."""
        error = UniFiRateLimitError("Too many requests")

        assert isinstance(error, UniFiAPIError)
        assert str(error) == "Too many requests"
        assert error.retry_after is None

    def test_rate_limit_error_with_retry_after(self):
        """Test rate limit error with retry_after parameter."""
        error = UniFiRateLimitError("Too many requests", retry_after=60)

        assert error.retry_after == 60


class TestUniFiNotFoundError:
    """Test UniFiNotFoundError exception."""

    def test_not_found_error(self):
        """Test not found error."""
        error = UniFiNotFoundError("Resource not found")

        assert isinstance(error, UniFiAPIError)
        assert "not found" in str(error).lower()


class TestUniFiConnectionError:
    """Test UniFiConnectionError exception."""

    def test_connection_error(self):
        """Test connection error."""
        error = UniFiConnectionError("Connection failed")

        assert isinstance(error, UniFiAPIError)
        assert "Connection failed" in str(error)


class TestUniFiValidationError:
    """Test UniFiValidationError exception."""

    def test_validation_error(self):
        """Test validation error."""
        error = UniFiValidationError("Invalid parameter")

        assert isinstance(error, UniFiAPIError)
        assert "Invalid parameter" in str(error)


class TestUniFiTimeoutError:
    """Test UniFiTimeoutError exception."""

    def test_timeout_error(self):
        """Test timeout error."""
        error = UniFiTimeoutError("Request timeout")

        assert isinstance(error, UniFiAPIError)
        assert "timeout" in str(error).lower()


class TestUniFiServerError:
    """Test UniFiServerError exception."""

    def test_server_error(self):
        """Test server error."""
        error = UniFiServerError("Internal server error")

        assert isinstance(error, UniFiAPIError)
        assert "server error" in str(error).lower()


class TestExceptionHierarchy:
    """Test exception class hierarchy."""

    def test_all_exceptions_inherit_from_base(self):
        """Test that all custom exceptions inherit from UniFiAPIError."""
        exception_classes = [
            UniFiAuthError,
            UniFiConnectionError,
            UniFiRateLimitError,
            UniFiNotFoundError,
            UniFiValidationError,
            UniFiTimeoutError,
            UniFiServerError,
        ]

        for exc_class in exception_classes:
            error = exc_class("Test")
            assert isinstance(error, UniFiAPIError)
            assert isinstance(error, Exception)

    def test_can_catch_all_with_base_exception(self):
        """Test that all exceptions can be caught with base class."""
        try:
            raise UniFiAuthError("Test")
        except UniFiAPIError as e:
            assert isinstance(e, UniFiAuthError)

        try:
            raise UniFiRateLimitError("Test", retry_after=30)
        except UniFiAPIError as e:
            assert isinstance(e, UniFiRateLimitError)
