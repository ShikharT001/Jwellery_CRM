"""
FastAPI dependency: organization context resolution.

This dependency resolves and validates the current user's membership
in a specific organization, providing an auditable organization context
for every request.
"""

from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.exceptions import (
    NotFoundError,
    OrganizationSuspendedError,
    UnauthorizedError,
)
from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.shared.models import Organization, OrganizationMember, User


def get_organization_membership(
    organization_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrganizationMember:
    """
    Verify that the current user is an active member of the specified organization.

    This dependency:
    1. Fetches the organization (404 if not found)
    2. Checks organization status (403 if suspended)
    3. Finds the user's membership record (403 if not a member)
    4. Verifies the membership is active (403 if suspended/deactivated)
    5. Returns the OrganizationMember record

    The organization_id ALWAYS comes from the URL path parameter,
    which is validated against the user's actual membership.
    Users cannot access organizations they don't belong to.
    """
    # 1. Fetch the organization
    organization = db.query(Organization).filter(
        Organization.id == organization_id
    ).first()

    if not organization:
        raise NotFoundError("Organization", str(organization_id))

    # 2. Check organization status
    if organization.status == "suspended":
        raise OrganizationSuspendedError()

    if organization.status in ("inactive",):
        raise UnauthorizedError(
            message="This organization is no longer active",
            error_code="ORGANIZATION_INACTIVE",
        )

    # 3. Find membership — Super Admins bypass this check
    if current_user.is_super_admin:
        # Super Admin gets a synthetic membership view for audit purposes
        # They can access any organization without being a member
        return _create_super_admin_membership_proxy(current_user, organization)

    membership = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == organization_id,
        OrganizationMember.user_id == current_user.id,
    ).first()

    if not membership:
        raise UnauthorizedError(
            message="You are not a member of this organization",
            error_code="NOT_A_MEMBER",
        )

    # 4. Check membership status
    if membership.status == "suspended":
        raise UnauthorizedError(
            message="Your access to this organization has been suspended",
            error_code="MEMBERSHIP_SUSPENDED",
        )

    if membership.status in ("deactivated", "invited"):
        raise UnauthorizedError(
            message="Your membership in this organization is not active",
            error_code="MEMBERSHIP_NOT_ACTIVE",
        )

    return membership


def _create_super_admin_membership_proxy(user: User, organization: Organization):
    """
    Create a synthetic membership object for Super Admin access.

    This allows Super Admins to access any organization's endpoints
    without needing an actual membership record. The proxy carries
    the organization reference for downstream use.
    """
    proxy = OrganizationMember()
    proxy.user_id = user.id
    proxy.organization_id = organization.id
    proxy.status = "active"
    proxy.organization = organization
    proxy.user = user
    proxy.member_roles = []
    return proxy
