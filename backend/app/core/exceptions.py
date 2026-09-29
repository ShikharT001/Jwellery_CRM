"""
Custom exception classes for the Jewellery ERP platform.

Using custom exceptions allows us to:
1. Catch specific error types in exception handlers
2. Attach structured metadata (status codes, error codes)
3. Keep business logic clean — raise exceptions, handle at the edge
"""

from typing import Any, Optional


class AppException(Exception):
    """Base exception for all application errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Any] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or "INTERNAL_ERROR"
        self.details = details
        super().__init__(message)


class AuthenticationError(AppException):
    """
    Raised when a request cannot be authenticated.

    Examples:
    - Missing or invalid JWT
    - Expired token
    - Malformed Authorization header
    """

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_FAILED",
        )


class UnauthorizedError(AppException):
    """
    Raised when an authenticated user is not allowed to perform an action.

    Examples:
    - User lacks required permission
    - User is not a member of the organization
    - Organization is suspended
    - Feature not available on the organization's subscription plan
    """

    def __init__(
        self,
        message: str = "You do not have permission to perform this action",
        error_code: str = "UNAUTHORIZED",
    ):
        super().__init__(
            message=message,
            status_code=403,
            error_code=error_code,
        )


ForbiddenError = UnauthorizedError


class NotFoundError(AppException):
    """
    Raised when a requested resource does not exist.
    """

    def __init__(self, resource: str = "Resource", resource_id: Optional[str] = None):
        message = f"{resource} not found"
        if resource_id:
            message = f"{resource} '{resource_id}' not found"
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND",
        )


class ConflictError(AppException):
    """
    Raised when an operation would create a duplicate or violate a uniqueness constraint.
    """

    def __init__(self, message: str = "A conflict occurred"):
        super().__init__(
            message=message,
            status_code=409,
            error_code="CONFLICT",
        )


class ValidationError(AppException):
    """
    Raised when business-level validation fails (not Pydantic schema validation).
    """

    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class FeatureNotAvailableError(UnauthorizedError):
    """
    Raised when an organization's subscription plan does not include the requested feature.
    """

    def __init__(self, feature_key: str):
        super().__init__(
            message=f"Feature '{feature_key}' is not available on your current subscription plan",
            error_code="FEATURE_NOT_AVAILABLE",
        )


class OrganizationSuspendedError(UnauthorizedError):
    """
    Raised when a request is made for a suspended organization.
    """

    def __init__(self):
        super().__init__(
            message="This organization has been suspended. Please contact support.",
            error_code="ORGANIZATION_SUSPENDED",
        )


class SuperAdminRequiredError(UnauthorizedError):
    """
    Raised when a Super Admin-only endpoint is accessed by a non-Super Admin.
    """

    def __init__(self):
        super().__init__(
            message="Super Admin access required",
            error_code="SUPER_ADMIN_REQUIRED",
        )
