"""
Feature access permission dependency.

This is the central authorization service for the platform.
Every API endpoint that touches feature-gated functionality
uses this dependency to verify access.

Authorization Precedence:
1. Platform safety checks (account status, org status)
2. Subscription validity
3. Organization-level feature override (Super Admin-set)
4. Plan feature entitlement
5. User role permission
"""

from typing import Callable
from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.exceptions import FeatureNotAvailableError, UnauthorizedError
from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.shared.models import (
    MemberRole,
    OrganizationFeatureOverride,
    OrganizationMember,
    OrganizationSubscription,
    Permission,
    PlanFeature,
    RolePermission,
    User,
)


def has_feature_access(
    db: Session,
    organization_id: UUID,
    user_id: UUID,
    feature_key: str,
    membership: OrganizationMember,
) -> bool:
    """
    Core authorization function.

    Checks whether a user in an organization has access to a specific feature.
    This function encapsulates all authorization logic so it can be used
    in both HTTP route dependencies and internal service calls.

    Returns:
        bool: True if access is granted, False otherwise

    This function does NOT raise exceptions — callers can decide what to do.
    For HTTP routes, use the require_feature() dependency factory instead.
    """
    # --- Step 1: Super Admins always have access ---
    user = db.query(User).filter(User.id == user_id).first()
    if user and user.is_super_admin:
        return True

    # --- Step 2: Check organization-level override (Super Admin may have set this) ---
    override = db.query(OrganizationFeatureOverride).filter(
        OrganizationFeatureOverride.organization_id == organization_id,
        OrganizationFeatureOverride.feature_key == feature_key,
    ).first()

    if override is not None:
        # An explicit override exists — it takes precedence over the plan
        if not override.enabled:
            return False  # Feature explicitly disabled for this org
        # Override is enabled — still need to check user role permission below

    else:
        # --- Step 3: Check subscription and plan entitlement ---
        active_subscription = db.query(OrganizationSubscription).filter(
            OrganizationSubscription.organization_id == organization_id,
            OrganizationSubscription.status.in_(["active", "trial"]),
        ).first()

        if not active_subscription:
            return False  # No active subscription

        plan_feature = db.query(PlanFeature).filter(
            PlanFeature.plan_id == active_subscription.plan_id,
            PlanFeature.feature_key == feature_key,
            PlanFeature.enabled == True,
        ).first()

        if not plan_feature:
            return False  # Feature not in plan

    # --- Step 4: Check user role has this permission ---
    # Get all role IDs for this member
    member_role_ids = [
        mr.role_id
        for mr in db.query(MemberRole).filter(
            MemberRole.member_id == membership.id
        ).all()
    ]

    if not member_role_ids:
        return False  # User has no roles assigned

    # Check if any of the member's roles grant this permission
    permission = db.query(Permission).filter(
        Permission.key == feature_key
    ).first()

    if not permission:
        return False  # Unknown permission key

    has_permission = db.query(RolePermission).filter(
        RolePermission.role_id.in_(member_role_ids),
        RolePermission.permission_id == permission.id,
    ).first()

    return has_permission is not None


def require_feature(feature_key: str) -> Callable:
    """
    FastAPI dependency factory for feature access control.

    Creates a dependency that raises 403 if the current user
    doesn't have access to the specified feature.

    Usage:
        @router.get("/inventory/items")
        def list_items(
            _: None = Depends(require_feature("inventory.view")),
            membership: OrganizationMember = Depends(get_organization_membership),
        ):
            ...

    Note: require_feature requires get_organization_membership to have
    already run (it's listed as a dependency above it in routes).
    """

    def _check_feature(
        membership: OrganizationMember,
        db: Session = Depends(get_db),
    ) -> None:
        allowed = has_feature_access(
            db=db,
            organization_id=membership.organization_id,
            user_id=membership.user_id,
            feature_key=feature_key,
            membership=membership,
        )
        if not allowed:
            raise FeatureNotAvailableError(feature_key)

    return _check_feature
