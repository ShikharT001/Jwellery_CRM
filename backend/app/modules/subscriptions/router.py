"""
Subscription Plans & Entitlements API Router.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_super_admin, get_current_user
from app.modules.subscriptions.schemas import (
    FeatureOverrideCreate,
    FeatureOverrideResponse,
    OrganizationSubscriptionCreate,
    OrganizationSubscriptionResponse,
    SubscriptionPlanCreate,
    SubscriptionPlanResponse,
    SubscriptionPlanUpdate,
)
from app.modules.subscriptions.service import SubscriptionService
from app.services.feature_access import FeatureAccessService
from app.shared.models import User
from app.shared.schemas import APIResponse

router = APIRouter(tags=["Subscription Plans & Entitlements"])


# ─────────────────────────────────────────────────
# Super Admin Plan Endpoints
# ─────────────────────────────────────────────────

@router.post(
    "/admin/subscription-plans",
    response_model=APIResponse[SubscriptionPlanResponse],
    status_code=201,
    summary="Create subscription plan (Super Admin)",
)
def create_subscription_plan(
    data: SubscriptionPlanCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_super_admin),
):
    service = SubscriptionService(db)
    plan = service.create_plan(data, actor)
    return APIResponse(
        success=True,
        message="Subscription plan created successfully",
        data=SubscriptionPlanResponse.model_validate(plan),
    )


@router.get(
    "/admin/subscription-plans",
    response_model=APIResponse[List[SubscriptionPlanResponse]],
    summary="List subscription plans (Super Admin)",
)
def list_subscription_plans(
    status: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_super_admin),
):
    service = SubscriptionService(db)
    plans = service.list_plans(status)
    return APIResponse(
        success=True,
        data=[SubscriptionPlanResponse.model_validate(p) for p in plans],
    )


@router.get(
    "/admin/subscription-plans/{plan_id}",
    response_model=APIResponse[SubscriptionPlanResponse],
    summary="Get subscription plan details (Super Admin)",
)
def get_subscription_plan(
    plan_id: UUID,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_super_admin),
):
    service = SubscriptionService(db)
    plan = service.get_plan(plan_id)
    return APIResponse(
        success=True,
        data=SubscriptionPlanResponse.model_validate(plan),
    )


@router.patch(
    "/admin/subscription-plans/{plan_id}",
    response_model=APIResponse[SubscriptionPlanResponse],
    summary="Update subscription plan (Super Admin)",
)
def update_subscription_plan(
    plan_id: UUID,
    data: SubscriptionPlanUpdate,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_super_admin),
):
    service = SubscriptionService(db)
    plan = service.update_plan(plan_id, data, actor)
    return APIResponse(
        success=True,
        message="Subscription plan updated successfully",
        data=SubscriptionPlanResponse.model_validate(plan),
    )


# ─────────────────────────────────────────────────
# Organization Subscription Assignment Endpoints
# ─────────────────────────────────────────────────

@router.post(
    "/admin/organizations/{organization_id}/subscription",
    response_model=APIResponse[OrganizationSubscriptionResponse],
    summary="Assign subscription plan to organization (Super Admin)",
)
def assign_organization_subscription(
    organization_id: UUID,
    data: OrganizationSubscriptionCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_super_admin),
):
    service = SubscriptionService(db)
    sub = service.assign_organization_subscription(organization_id, data, actor)
    return APIResponse(
        success=True,
        message="Subscription plan assigned successfully",
        data=OrganizationSubscriptionResponse.model_validate(sub),
    )


@router.get(
    "/admin/organizations/{organization_id}/subscription",
    response_model=APIResponse[Optional[OrganizationSubscriptionResponse]],
    summary="Get organization active subscription (Super Admin)",
)
def get_organization_subscription(
    organization_id: UUID,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_super_admin),
):
    service = SubscriptionService(db)
    sub = service.get_organization_subscription(organization_id)
    return APIResponse(
        success=True,
        data=OrganizationSubscriptionResponse.model_validate(sub) if sub else None,
    )


@router.post(
    "/admin/organizations/{organization_id}/feature-overrides",
    response_model=APIResponse[FeatureOverrideResponse],
    summary="Set organization feature override (Super Admin)",
)
def set_feature_override(
    organization_id: UUID,
    data: FeatureOverrideCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_super_admin),
):
    service = SubscriptionService(db)
    override = service.set_feature_override(organization_id, data, actor)
    return APIResponse(
        success=True,
        message="Feature override configured successfully",
        data=FeatureOverrideResponse.model_validate(override),
    )


@router.get(
    "/admin/organizations/{organization_id}/feature-overrides",
    response_model=APIResponse[List[FeatureOverrideResponse]],
    summary="List organization feature overrides (Super Admin)",
)
def list_feature_overrides(
    organization_id: UUID,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_super_admin),
):
    service = SubscriptionService(db)
    overrides = service.get_organization_overrides(organization_id)
    return APIResponse(
        success=True,
        data=[FeatureOverrideResponse.model_validate(o) for o in overrides],
    )


# ─────────────────────────────────────────────────
# Centralized Organization Features Access Endpoint
# ─────────────────────────────────────────────────

@router.get(
    "/organizations/{organization_id}/features",
    summary="Get authenticated user's effective feature entitlements & permissions",
)
def get_effective_organization_features(
    organization_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = FeatureAccessService(db)
    access_info = service.evaluate_access(user, organization_id)
    return APIResponse(
        success=True,
        data=access_info,
    )
