"""
Retry logic with exponential backoff for API requests.

This module provides decorators and utilities for handling transient failures
when making API requests.
"""

import logging
import time
from functools import wraps
from typing import Callable, Tuple, Type

from src.exceptions import UniFiConnectionError, UniFiRateLimitError, UniFiServerError

logger = logging.getLogger(__name__)


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    retry_on: Tuple[Type[Exception], ...] = (
        UniFiRateLimitError,
        UniFiServerError,
        UniFiConnectionError,
    ),
):
    """
    Decorator to retry a function with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        base_delay: Initial delay in seconds (default: 1.0)
        max_delay: Maximum delay in seconds (default: 60.0)
        exponential_base: Base for exponential calculation (default: 2.0)
        retry_on: Tuple of exception types to retry on

    Returns:
        Decorated function with retry logic

    Example:
        @retry_with_backoff(max_retries=3)
        def make_api_call():
            # Your API call here
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            func_name = getattr(func, "__name__", repr(func))  # Safe name extraction

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)

                except retry_on as e:
                    last_exception = e

                    # Don't retry if this was the last attempt
                    if attempt == max_retries:
                        logger.error(
                            f"Max retries ({max_retries}) reached for " f"{func_name}"
                        )
                        raise

                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (exponential_base**attempt), max_delay)

                    # Use Retry-After header if available
                    if isinstance(e, UniFiRateLimitError) and e.retry_after:
                        delay = min(e.retry_after, max_delay)

                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed for "
                        f"{func_name}: {str(e)}. "
                        f"Retrying in {delay:.1f} seconds..."
                    )

                    time.sleep(delay)

                except Exception as e:
                    # Don't retry on other exceptions
                    logger.error(f"Non-retryable error in {func_name}: {str(e)}")
                    raise

            # Should never reach here, but just in case
            if last_exception:
                raise last_exception

        return wrapper

    return decorator


def should_retry(status_code: int) -> bool:
    """
    Determine if a request should be retried based on status code.

    Args:
        status_code: HTTP status code

    Returns:
        True if request should be retried, False otherwise
    """
    # Retry on rate limiting
    if status_code == 429:
        return True

    # Retry on server errors (5xx)
    if 500 <= status_code < 600:
        return True

    # Retry on specific client errors that might be transient
    if status_code in (408, 502, 503, 504):  # Request Timeout, Bad Gateway, etc.
        return True

    return False


def get_retry_delay(response) -> float:
    """
    Extract retry delay from response headers.

    Args:
        response: requests.Response object

    Returns:
        Delay in seconds, or 0 if no Retry-After header
    """
    retry_after = response.headers.get("Retry-After")

    if not retry_after:
        return 0.0

    try:
        # Retry-After can be in seconds or HTTP date format
        return float(retry_after)
    except ValueError:
        # If it's a date, just return a default delay
        return 60.0
