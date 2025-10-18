"""
Unit tests for retry logic and exponential backoff.

Tests the retry decorator and helper functions.
"""

import time
from unittest.mock import Mock, patch

import pytest

from src.exceptions import UniFiConnectionError, UniFiRateLimitError, UniFiServerError
from src.retry import get_retry_delay, retry_with_backoff, should_retry


class TestShouldRetry:
    """Test should_retry function."""

    def test_should_retry_on_429(self):
        """Test that 429 (rate limit) should retry."""
        assert should_retry(429) is True

    def test_should_retry_on_500(self):
        """Test that 500 (server error) should retry."""
        assert should_retry(500) is True

    def test_should_retry_on_503(self):
        """Test that 503 (service unavailable) should retry."""
        assert should_retry(503) is True

    def test_should_not_retry_on_200(self):
        """Test that 200 (OK) should not retry."""
        assert should_retry(200) is False

    def test_should_not_retry_on_400(self):
        """Test that 400 (bad request) should not retry."""
        assert should_retry(400) is False

    def test_should_not_retry_on_404(self):
        """Test that 404 (not found) should not retry."""
        assert should_retry(404) is False

    def test_should_retry_on_408(self):
        """Test that 408 (request timeout) should retry."""
        assert should_retry(408) is True

    def test_should_retry_on_502(self):
        """Test that 502 (bad gateway) should retry."""
        assert should_retry(502) is True


class TestGetRetryDelay:
    """Test get_retry_delay function."""

    def test_get_retry_delay_from_header(self):
        """Test extracting retry delay from Retry-After header."""
        mock_response = Mock()
        mock_response.headers = {"Retry-After": "60"}

        delay = get_retry_delay(mock_response)

        assert delay == 60.0

    def test_get_retry_delay_no_header(self):
        """Test when Retry-After header is missing."""
        mock_response = Mock()
        mock_response.headers = {}

        delay = get_retry_delay(mock_response)

        assert delay == 0.0

    def test_get_retry_delay_date_format(self):
        """Test when Retry-After is in date format."""
        mock_response = Mock()
        mock_response.headers = {"Retry-After": "Wed, 21 Oct 2025 07:28:00 GMT"}

        delay = get_retry_delay(mock_response)

        # Should return default delay for date format
        assert delay == 60.0


class TestRetryWithBackoff:
    """Test retry_with_backoff decorator."""

    def test_successful_call_no_retry(self):
        """Test that successful calls don't retry."""
        mock_func = Mock(return_value="success")
        decorated = retry_with_backoff()(mock_func)

        result = decorated()

        assert result == "success"
        assert mock_func.call_count == 1

    def test_retry_on_rate_limit_error(self):
        """Test retrying on rate limit errors."""
        mock_func = Mock(side_effect=[UniFiRateLimitError("Rate limit"), "success"])
        decorated = retry_with_backoff(max_retries=2, base_delay=0.1)(mock_func)

        result = decorated()

        assert result == "success"
        assert mock_func.call_count == 2

    def test_retry_on_server_error(self):
        """Test retrying on server errors."""
        mock_func = Mock(side_effect=[UniFiServerError("Server error"), "success"])
        decorated = retry_with_backoff(max_retries=2, base_delay=0.1)(mock_func)

        result = decorated()

        assert result == "success"
        assert mock_func.call_count == 2

    def test_retry_on_connection_error(self):
        """Test retrying on connection errors."""
        mock_func = Mock(
            side_effect=[UniFiConnectionError("Connection failed"), "success"]
        )
        decorated = retry_with_backoff(max_retries=2, base_delay=0.1)(mock_func)

        result = decorated()

        assert result == "success"
        assert mock_func.call_count == 2

    def test_max_retries_exceeded(self):
        """Test that max retries is respected."""
        mock_func = Mock(side_effect=UniFiServerError("Server error"))
        decorated = retry_with_backoff(max_retries=2, base_delay=0.1)(mock_func)

        with pytest.raises(UniFiServerError):
            decorated()

        # Should try initial + 2 retries = 3 times
        assert mock_func.call_count == 3

    def test_exponential_backoff_delay(self):
        """Test that delay increases exponentially."""
        mock_func = Mock(
            side_effect=[
                UniFiServerError("Error"),
                UniFiServerError("Error"),
                "success",
            ]
        )

        decorated = retry_with_backoff(
            max_retries=3, base_delay=0.1, exponential_base=2.0
        )(mock_func)

        start_time = time.time()
        result = decorated()
        elapsed = time.time() - start_time

        # Should wait 0.1 + 0.2 = 0.3 seconds minimum
        assert elapsed >= 0.3
        assert result == "success"

    def test_max_delay_cap(self):
        """Test that delay is capped at max_delay."""
        mock_func = Mock(side_effect=[UniFiServerError("Error"), "success"])

        decorated = retry_with_backoff(
            max_retries=2,
            base_delay=100.0,  # Very high base
            max_delay=0.2,  # But capped at 0.2
        )(mock_func)

        start_time = time.time()
        result = decorated()
        elapsed = time.time() - start_time

        # Should be capped at 0.2 seconds
        assert elapsed < 0.5
        assert result == "success"

    def test_non_retryable_error(self):
        """Test that non-retryable errors are not retried."""
        mock_func = Mock(side_effect=ValueError("Not retryable"))
        decorated = retry_with_backoff(max_retries=2)(mock_func)

        with pytest.raises(ValueError):
            decorated()

        # Should only be called once
        assert mock_func.call_count == 1

    def test_retry_after_header_respected(self):
        """Test that Retry-After from rate limit is respected."""
        error = UniFiRateLimitError("Rate limit", retry_after=0.2)
        mock_func = Mock(side_effect=[error, "success"])

        decorated = retry_with_backoff(max_retries=2, base_delay=10.0)(  # High base
            mock_func
        )

        start_time = time.time()
        result = decorated()
        elapsed = time.time() - start_time

        # Should use retry_after (0.2) instead of calculated delay
        assert 0.2 <= elapsed < 0.5
        assert result == "success"

    def test_preserves_function_metadata(self):
        """Test that decorator preserves function metadata."""

        @retry_with_backoff()
        def test_function():
            """Test docstring."""
            return "test"

        assert test_function.__name__ == "test_function"
        assert test_function.__doc__ == "Test docstring."


class TestRetryIntegration:
    """Integration tests for retry logic."""

    def test_multiple_retries_with_increasing_delays(self):
        """Test multiple retries with increasing delays."""
        attempts = []

        def failing_function():
            attempts.append(time.time())
            if len(attempts) < 3:
                raise UniFiServerError("Error")
            return "success"

        decorated = retry_with_backoff(
            max_retries=3, base_delay=0.1, exponential_base=2.0
        )(failing_function)

        result = decorated()

        assert result == "success"
        assert len(attempts) == 3

        # Check delays increased
        if len(attempts) >= 2:
            delay1 = attempts[1] - attempts[0]
            assert delay1 >= 0.1  # First retry delay

        if len(attempts) >= 3:
            delay2 = attempts[2] - attempts[1]
            assert delay2 >= 0.2  # Second retry delay (2^1 * 0.1)
