"""
Custom exceptions for the UniFi API client.

This module defines specific exception types for different error scenarios
that can occur when interacting with the UniFi API.
"""


class UniFiAPIError(Exception):
    """
    Base exception for all UniFi API errors.

    All other UniFi exceptions inherit from this base class.
    """

    def __init__(self, message: str, response=None):
        """
        Initialize the exception.

        Args:
            message: Error message describing what went wrong
            response: Optional requests.Response object for detailed error info
        """
        super().__init__(message)
        self.message = message
        self.response = response
        self.status_code = response.status_code if response else None


class UniFiAuthError(UniFiAPIError):
    """
    Authentication failed.

    Raised when the API key is invalid, missing, or expired.

    Recovery:
        - Verify your API key is correct
        - Check if the API key has been revoked
        - Generate a new API key if needed
    """

    pass


class UniFiConnectionError(UniFiAPIError):
    """
    Network connection error.

    Raised when unable to connect to the UniFi API server.

    Recovery:
        - Check your internet connection
        - Verify the API base URL is correct
        - Check if the UniFi API service is up
    """

    pass


class UniFiRateLimitError(UniFiAPIError):
    """
    API rate limit exceeded.

    Raised when too many requests have been made in a short time period.

    Recovery:
        - Wait before making more requests
        - Implement exponential backoff
        - Reduce request frequency
        - Consider caching responses
    """

    def __init__(self, message: str, response=None, retry_after: int = None):
        """
        Initialize rate limit exception.

        Args:
            message: Error message
            response: Optional requests.Response object
            retry_after: Seconds to wait before retrying (from Retry-After header)
        """
        super().__init__(message, response)
        self.retry_after = retry_after


class UniFiNotFoundError(UniFiAPIError):
    """
    Resource not found.

    Raised when the requested resource (host, device, etc.) doesn't exist.

    Recovery:
        - Verify the resource ID is correct
        - Check if the resource has been deleted
        - List available resources first
    """

    pass


class UniFiValidationError(UniFiAPIError):
    """
    Invalid request parameters.

    Raised when request parameters fail validation before sending to the API.

    Recovery:
        - Check parameter types and values
        - Review API documentation for correct format
        - Validate input data before making requests
    """

    pass


class UniFiTimeoutError(UniFiAPIError):
    """
    Request timeout.

    Raised when a request takes too long to complete.

    Recovery:
        - Increase timeout value
        - Check network latency
        - Try again later
    """

    pass


class UniFiServerError(UniFiAPIError):
    """
    Server-side error (5xx responses).

    Raised when the UniFi API server encounters an error.

    Recovery:
        - Wait and retry with exponential backoff
        - Check UniFi service status
        - Report if error persists
    """

    pass
