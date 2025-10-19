"""Error handling middleware."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class APIError(Exception):
    """Base API error."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(APIError):
    """Resource not found error."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class ValidationError(APIError):
    """Validation error."""

    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)


class AuthenticationError(APIError):
    """Authentication error."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


def add_exception_handlers(app: FastAPI) -> None:
    """Add exception handlers to FastAPI app."""

    @app.exception_handler(APIError)
    async def api_error_handler(request: Request, exc: APIError):
        """Handle API errors."""
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.message},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected errors."""
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Internal server error"},
        )
