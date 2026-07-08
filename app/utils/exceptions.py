from fastapi import status
from typing import Optional, Any, Dict

from starlette.exceptions import HTTPException


class APPException(HTTPException):
    """Custom API Exception class that extends HTTPException"""

    def __init__(
        self,
        status_code: int,
        message: str = "An error occurred",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.details = details or {}
        super().__init__(status_code=status_code, detail=message)


class AuthenticationException(APPException):
    """Authentication related errors"""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, message=message)


class AuthorizationException(APPException):
    """Authorization related errors"""

    def __init__(self, message: str = "Access denied"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, message=message)


class ValidationException(APPException):
    """Validation related errors"""

    def __init__(
        self,
        message: str = "Validation failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, message=message, details=details
        )


class NotFoundException(APPException):
    """Not found errors"""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, message=message)


class ConflictException(APPException):
    """Conflict errors (duplicate resource, etc.)"""

    def __init__(self, message: str = "Resource conflict"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, message=message)


class ServerException(APPException):
    """Internal server errors"""

    def __init__(self, message: str = "Internal server error"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message=message
        )
