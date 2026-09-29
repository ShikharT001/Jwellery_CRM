"""
Feature Access Control Service.

Evaluates feature entitlements and capabilities for organizations and users
based on subscription plans, per-organization overrides, and member roles.
"""

from typing import Dict, Any, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.shared.models import (
    Organization,
    OrganizationSubscription,
    PlanFeature,
    OrganizationFeatureOverride,
    OrganizationMember,
    MemberRole,
    RolePermission,
    Permission,
    User,
)
from app.core.exceptions import UnauthorizedError, ForbiddenError, OrganizationSuspendedError


class FeatureAccessService:
    def __init__(self, db: Session):
        self.db = db

    def get_organization_effective_features(self, organization_id: UUID) -> Dict[str, Dict[str, Any]]:
        """
        Calculates all effective feature entitlements for an organization.
        
        Precedence:
        1. Base plan features (from active OrganizationSubscription)
        2. Per-organization overrides (OrganizationFeatureOverride) - overrides base plan
        """
        # 1. Fetch active subscription
        subscription = (
            self.db.query(OrganizationSubscription)
            .filter(
                OrganizationSubscription.organization_id == organization_id,
                OrganizationSubscription.status.in_(["active", "trial"]),
            )
            .order_by(OrganizationSubscription.created_at.desc())
            .first()
        )

        effective_features: Dict[str, Dict[str, Any]] = {}

        if subscription and subscription.plan:
            # Load plan features
            for feature in subscription.plan.features:
                effective_features[feature.feature_key] = {
                    "enabled": feature.enabled,
                    "limit_value": feature.limit_value,
                    "source": "subscription_plan",
                }

        # 2. Apply organization-level feature overrides
        overrides = (
            self.db.query(OrganizationFeatureOverride)
            .filter(OrganizationFeatureOverride.organization_id == organization_id)
            .all()
        )

        for override in overrides:
            effective_features[override.feature_key] = {
                "enabled": override.enabled,
                "limit_value": override.limit_value,
                "source": "organization_override",
                "reason": override.reason,
            }

        return effective_features

    def get_user_effective_permissions(self, user_id: UUID, organization_id: UUID) -> List[str]:
        """
        Returns all permission keys granted to a user within a specific organization
        based on their assigned roles.
        """
        # Find membership
        member = (
            self.db.query(OrganizationMember)
            .filter(
                OrganizationMember.user_id == user_id,
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.status == "active",
            )
            .first()
        )

        if not member:
            return []

        # Find member roles
        member_roles = (
            self.db.query(MemberRole)
            .filter(MemberRole.member_id == member.id)
            .all()
        )

        role_ids = [mr.role_id for mr in member_roles]
        if not role_ids:
            return []

        # Find permissions for roles
        permissions = (
            self.db.query(Permission.key)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .filter(RolePermission.role_id.in_(role_ids))
            .distinct()
            .all()
        )

        return [p.key for p in permissions]

    def evaluate_access(
        self, user: User, organization_id: UUID, feature_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluates complete feature and permission access for a user in an organization.
        
        Returns:
            Dict containing effective features and granted permissions.
        """
        # Super admin bypasses organization constraints for platform management
        if user.is_super_admin:
            all_features = self.get_organization_effective_features(organization_id)
            return {
                "organization_id": str(organization_id),
                "is_super_admin": True,
                "features": all_features,
                "permissions": ["*"],
            }

        # 1. Organization status check
        org = self.db.query(Organization).filter(Organization.id == organization_id).first()
        if not org:
            raise ForbiddenError("Organization not found")
        if org.status == "suspended":
            raise OrganizationSuspendedError("Organization access is suspended")
        if org.status != "active" and org.status != "trial":
            raise ForbiddenError(f"Organization status is '{org.status}'")

        # 2. Member status check
        member = (
            self.db.query(OrganizationMember)
            .filter(
                OrganizationMember.user_id == user.id,
                OrganizationMember.organization_id == organization_id,
            )
            .first()
        )
        if not member or member.status != "active":
            raise ForbiddenError("User is not an active member of this organization")

        # 3. Effective features & permissions
        effective_features = self.get_organization_effective_features(organization_id)
        user_permissions = self.get_user_effective_permissions(user.id, organization_id)

        return {
            "organization_id": str(organization_id),
            "is_super_admin": False,
            "features": effective_features,
            "permissions": user_permissions,
        }
