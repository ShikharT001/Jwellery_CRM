"""
Shared Pydantic schemas used across multiple modules.

These are response envelopes, pagination helpers, and utility types
that are used throughout the API.
"""

from typing import Generic, List, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """
    Standard API response envelope.

    All list and detail endpoints should wrap their data in this shape
    for consistency. Clients can always check success/error the same way.
    """

    success: bool = True
    message: Optional[str] = None
    data: Optional[T] = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated list response."""

    success: bool = True
    data: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int

    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    """Standard error response body."""

    success: bool = False
    error_code: str
    message: str
    details: Optional[object] = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    database: str
    version: str
    environment: str
