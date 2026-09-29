"""
Pydantic schemas for the Organization module.

These define the exact shape of request bodies and response payloads
for organization-related API endpoints.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# ─────────────────────────────────────────────────
# Organization Schemas
# ─────────────────────────────────────────────────

class OrganizationCreate(BaseModel):
    """Request body for creating a new organization."""

    name: str = Field(..., min_length=2, max_length=255)
    legal_name: Optional[str] = Field(None, max_length=255)
    slug: str = Field(
        ...,
        min_length=3,
        max_length=100,
        pattern=r"^[a-z0-9-]+$",
        description="URL-safe identifier: lowercase letters, numbers, and hyphens only",
    )
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    country: str = Field(default="India", max_length=100)
    currency: str = Field(default="INR", max_length=10)


class OrganizationUpdate(BaseModel):
    """Request body for updating an organization. All fields optional."""

    name: Optional[str] = Field(None, min_length=2, max_length=255)
    legal_name: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    country: Optional[str] = Field(None, max_length=100)
    currency: Optional[str] = Field(None, max_length=10)


class OrganizationStatusUpdate(BaseModel):
    """Request body for changing organization status (Super Admin only)."""

    status: str = Field(..., description="One of: active, suspended, trial, inactive")
    reason: Optional[str] = Field(None, description="Reason for status change (logged in audit)")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed = ("active", "suspended", "trial", "inactive")
        if v not in allowed:
            raise ValueError(f"status must be one of: {', '.join(allowed)}")
        return v


class OrganizationResponse(BaseModel):
    """Response schema for a single organization."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    legal_name: Optional[str]
    slug: str
    email: Optional[str]
    phone: Optional[str]
    country: str
    currency: str
    status: str
    created_at: datetime
    updated_at: datetime


class OrganizationListResponse(BaseModel):
    """Response schema for a list of organizations."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    email: Optional[str]
    status: str
    country: str
    currency: str
    created_at: datetime


# ─────────────────────────────────────────────────
# Branch Schemas
# ─────────────────────────────────────────────────

class BranchCreate(BaseModel):
    """Request body for creating a branch."""

    name: str = Field(..., min_length=1, max_length=255)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    phone: Optional[str] = Field(None, max_length=50)
    is_head_office: bool = False


class BranchUpdate(BaseModel):
    """Request body for updating a branch."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    phone: Optional[str] = Field(None, max_length=50)
    is_head_office: Optional[bool] = None
    status: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ("active", "inactive", "closed"):
            raise ValueError("status must be one of: active, inactive, closed")
        return v


class BranchResponse(BaseModel):
    """Response schema for a branch."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    name: str
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    postal_code: Optional[str]
    phone: Optional[str]
    is_head_office: bool
    status: str
    created_at: datetime
    updated_at: datetime


# ─────────────────────────────────────────────────
# Member Schemas
# ─────────────────────────────────────────────────

class MemberResponse(BaseModel):
    """Response schema for an organization member."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    user_id: UUID
    status: str
    joined_at: Optional[str]
