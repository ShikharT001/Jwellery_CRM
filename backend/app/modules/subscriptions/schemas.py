"""
Subscription Plans and Entitlements Pydantic Schemas.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ─────────────────────────────────────────────────
# Plan Feature Schemas
# ─────────────────────────────────────────────────

class PlanFeatureBase(BaseModel):
    feature_key: str = Field(..., max_length=100, example="inventory.view")
    enabled: bool = True
    limit_value: Optional[int] = None


class PlanFeatureCreate(PlanFeatureBase):
    pass


class PlanFeatureResponse(PlanFeatureBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    plan_id: UUID


# ─────────────────────────────────────────────────
# Subscription Plan Schemas
# ─────────────────────────────────────────────────

class SubscriptionPlanBase(BaseModel):
    name: str = Field(..., max_length=255, example="PRO")
    description: Optional[str] = None
    price_monthly: Optional[float] = 0.0
    price_yearly: Optional[float] = 0.0
    currency: str = Field(default="INR", max_length=10)
    status: str = Field(default="active", example="active")


class SubscriptionPlanCreate(SubscriptionPlanBase):
    features: Optional[List[PlanFeatureCreate]] = []


class SubscriptionPlanUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price_monthly: Optional[float] = None
    price_yearly: Optional[float] = None
    status: Optional[str] = None
    features: Optional[List[PlanFeatureCreate]] = None


class SubscriptionPlanResponse(SubscriptionPlanBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    features: List[PlanFeatureResponse] = []
    created_at: datetime
    updated_at: datetime


# ─────────────────────────────────────────────────
# Organization Subscription Schemas
# ─────────────────────────────────────────────────

class OrganizationSubscriptionCreate(BaseModel):
    plan_id: UUID
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None


class OrganizationSubscriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    plan_id: UUID
    status: str
    starts_at: datetime
    ends_at: Optional[datetime] = None
    plan: Optional[SubscriptionPlanResponse] = None
    created_at: datetime


# ─────────────────────────────────────────────────
# Organization Feature Override Schemas
# ─────────────────────────────────────────────────

class FeatureOverrideCreate(BaseModel):
    feature_key: str = Field(..., max_length=100)
    enabled: bool
    limit_value: Optional[int] = None
    reason: Optional[str] = None


class FeatureOverrideResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    feature_key: str
    enabled: bool
    limit_value: Optional[int] = None
    reason: Optional[str] = None
    created_by: Optional[UUID] = None
    created_at: datetime
