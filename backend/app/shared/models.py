"""
Platform-level SQLAlchemy ORM models.

These models map to the core database tables that power the multi-tenant
platform. Every model uses UUID primary keys and (where appropriate)
inherits the TimestampMixin for automatic created_at / updated_at tracking.
"""

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


# ─────────────────────────────────────────────────
# User
# ─────────────────────────────────────────────────

class User(Base, TimestampMixin):
    """
    Application user profile, linked to a Supabase Auth user.

    Supabase owns authentication (passwords, MFA, email verification).
    We own the application profile (display name, status, is_super_admin).

    The supabase_user_id is the UUID that Supabase generates in auth.users.
    We use it to look up our users record after verifying a JWT.
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    supabase_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, nullable=False, index=True
    )
    display_name: Mapped[Optional[str]] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    is_super_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'suspended', 'deactivated')",
            name="ck_users_status",
        ),
        Index("idx_users_email", "email"),
        Index("idx_users_supabase_user_id", "supabase_user_id"),
    )

    # Relationships
    memberships: Mapped[List["OrganizationMember"]] = relationship(
        "OrganizationMember", back_populates="user"
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog", back_populates="actor_user"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"


# ─────────────────────────────────────────────────
# Organization
# ─────────────────────────────────────────────────

class Organization(Base, TimestampMixin):
    """
    A jewellery store tenant on the platform.

    Each organization is fully isolated. All tenant-scoped data
    (inventory, customers, sales, etc.) is filtered by organization_id.

    status values:
    - active:    Organization is operational
    - trial:     Organization is in a free trial period
    - suspended: Access is blocked (non-payment, policy violation, etc.)
    - inactive:  Organization has been deactivated
    """

    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    legal_name: Mapped[Optional[str]] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    country: Mapped[str] = mapped_column(String(100), default="India", nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="active"
    )
    settings: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)

    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'trial', 'suspended', 'inactive')",
            name="ck_organizations_status",
        ),
        Index("idx_organizations_slug", "slug", unique=True),
        Index("idx_organizations_status", "status"),
    )

    # Relationships
    branches: Mapped[List["Branch"]] = relationship(
        "Branch", back_populates="organization"
    )
    members: Mapped[List["OrganizationMember"]] = relationship(
        "OrganizationMember", back_populates="organization"
    )
    roles: Mapped[List["Role"]] = relationship(
        "Role", back_populates="organization"
    )
    subscriptions: Mapped[List["OrganizationSubscription"]] = relationship(
        "OrganizationSubscription", back_populates="organization"
    )
    feature_overrides: Mapped[List["OrganizationFeatureOverride"]] = relationship(
        "OrganizationFeatureOverride", back_populates="organization"
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog", back_populates="organization"
    )

    def __repr__(self) -> str:
        return f"<Organization id={self.id} slug={self.slug}>"


# ─────────────────────────────────────────────────
# Branch
# ─────────────────────────────────────────────────

class Branch(Base, TimestampMixin):
    """
    A physical branch (location) of a jewellery store.

    One organization can have many branches. Inventory items
    are always associated with a specific branch.
    """

    __tablename__ = "branches"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(Text)
    city: Mapped[Optional[str]] = mapped_column(String(100))
    state: Mapped[Optional[str]] = mapped_column(String(100))
    postal_code: Mapped[Optional[str]] = mapped_column(String(20))
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    is_head_office: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="active"
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'inactive', 'closed')",
            name="ck_branches_status",
        ),
        Index("idx_branches_organization_id", "organization_id"),
        Index("idx_branches_status", "organization_id", "status"),
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="branches"
    )

    def __repr__(self) -> str:
        return f"<Branch id={self.id} name={self.name}>"


# ─────────────────────────────────────────────────
# Organization Membership
# ─────────────────────────────────────────────────

class OrganizationMember(Base):
    """
    Links a User to an Organization.

    A user can be a member of multiple organizations (e.g., a consultant
    managing multiple stores). Each membership is independent — the user
    has a separate role in each organization.

    status values:
    - active:      Member has full access (subject to role permissions)
    - invited:     Invitation sent, user hasn't accepted yet
    - suspended:   Access temporarily blocked by the org owner
    - deactivated: Permanently removed from the organization
    """

    __tablename__ = "organization_members"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="active"
    )
    joined_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'suspended', 'invited', 'deactivated')",
            name="ck_org_members_status",
        ),
        UniqueConstraint("organization_id", "user_id", name="uq_org_member"),
        Index("idx_org_members_user_id", "user_id"),
        Index("idx_org_members_org_id", "organization_id"),
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="members"
    )
    user: Mapped["User"] = relationship("User", back_populates="memberships")
    member_roles: Mapped[List["MemberRole"]] = relationship(
        "MemberRole", back_populates="member"
    )

    def __repr__(self) -> str:
        return f"<OrganizationMember user={self.user_id} org={self.organization_id}>"


# ─────────────────────────────────────────────────
# Roles & Permissions
# ─────────────────────────────────────────────────

class Role(Base):
    """
    A named set of permissions.

    System roles (organization_id IS NULL, is_system_role=True):
    - ORGANIZATION_OWNER
    - BRANCH_MANAGER
    - SALES_STAFF
    - INVENTORY_MANAGER
    - ACCOUNTANT
    - WORKSHOP_MANAGER

    Custom roles (organization_id IS NOT NULL):
    - Created by organization owners for their specific needs
    """

    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_system_role: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("organization_id", "name", name="uq_role_name_per_org"),
        Index("idx_roles_organization_id", "organization_id"),
    )

    # Relationships
    organization: Mapped[Optional["Organization"]] = relationship(
        "Organization", back_populates="roles"
    )
    role_permissions: Mapped[List["RolePermission"]] = relationship(
        "RolePermission", back_populates="role"
    )
    member_roles: Mapped[List["MemberRole"]] = relationship(
        "MemberRole", back_populates="role"
    )

    def __repr__(self) -> str:
        return f"<Role name={self.name}>"


class Permission(Base):
    """
    A single capability key in the system.

    Examples: 'inventory.view', 'sales.create', 'reports.financial'

    Permissions are seeded at deployment time — they map to specific
    functionality in the application.
    """

    __tablename__ = "permissions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    module: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("idx_permissions_key", "key"),
        Index("idx_permissions_module", "module"),
    )

    role_permissions: Mapped[List["RolePermission"]] = relationship(
        "RolePermission", back_populates="permission"
    )

    def __repr__(self) -> str:
        return f"<Permission key={self.key}>"


class RolePermission(Base):
    """
    Many-to-many join between Role and Permission.
    Defines which permissions a role grants.
    """

    __tablename__ = "role_permissions"

    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    permission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    )

    __table_args__ = (
        Index("idx_role_permissions_role_id", "role_id"),
    )

    role: Mapped["Role"] = relationship("Role", back_populates="role_permissions")
    permission: Mapped["Permission"] = relationship(
        "Permission", back_populates="role_permissions"
    )


class MemberRole(Base):
    """
    Assigns a role to an organization member.
    A member can have multiple roles within one organization.
    """

    __tablename__ = "member_roles"

    member_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organization_members.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    )

    __table_args__ = (
        Index("idx_member_roles_member_id", "member_id"),
    )

    member: Mapped["OrganizationMember"] = relationship(
        "OrganizationMember", back_populates="member_roles"
    )
    role: Mapped["Role"] = relationship("Role", back_populates="member_roles")


# ─────────────────────────────────────────────────
# Subscription Tables (Phase 3 — models only for migrations)
# ─────────────────────────────────────────────────

class SubscriptionPlan(Base, TimestampMixin):
    """A subscription plan available on the platform."""

    __tablename__ = "subscription_plans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    price_monthly: Mapped[Optional[float]] = mapped_column(nullable=True)
    price_yearly: Mapped[Optional[float]] = mapped_column(nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)

    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'inactive', 'deprecated')",
            name="ck_subscription_plans_status",
        ),
    )

    features: Mapped[List["PlanFeature"]] = relationship(
        "PlanFeature", back_populates="plan"
    )
    subscriptions: Mapped[List["OrganizationSubscription"]] = relationship(
        "OrganizationSubscription", back_populates="plan"
    )


class PlanFeature(Base):
    """A feature entitlement within a subscription plan."""

    __tablename__ = "plan_features"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("subscription_plans.id", ondelete="CASCADE"),
        nullable=False,
    )
    feature_key: Mapped[str] = mapped_column(String(100), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    limit_value: Mapped[Optional[int]] = mapped_column(nullable=True)

    __table_args__ = (
        UniqueConstraint("plan_id", "feature_key", name="uq_plan_feature"),
        Index("idx_plan_features_plan_id", "plan_id"),
    )

    plan: Mapped["SubscriptionPlan"] = relationship(
        "SubscriptionPlan", back_populates="features"
    )


class OrganizationSubscription(Base, TimestampMixin):
    """An organization's active subscription to a plan."""

    __tablename__ = "organization_subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("subscription_plans.id"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'expired', 'cancelled', 'trial')",
            name="ck_org_subscriptions_status",
        ),
        Index("idx_org_subscriptions_org_id", "organization_id"),
    )

    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="subscriptions"
    )
    plan: Mapped["SubscriptionPlan"] = relationship(
        "SubscriptionPlan", back_populates="subscriptions"
    )


class OrganizationFeatureOverride(Base, TimestampMixin):
    """
    Super Admin-controlled per-organization feature overrides.

    These take precedence over plan entitlements.
    A Super Admin can enable a feature that isn't in the plan (grace period),
    or disable a feature that is in the plan (compliance block).
    """

    __tablename__ = "organization_feature_overrides"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    feature_key: Mapped[str] = mapped_column(String(100), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False)
    limit_value: Mapped[Optional[int]] = mapped_column(nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(Text)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    __table_args__ = (
        UniqueConstraint(
            "organization_id", "feature_key", name="uq_org_feature_override"
        ),
        Index("idx_feature_overrides_org_id", "organization_id"),
    )

    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="feature_overrides"
    )


# ─────────────────────────────────────────────────
# Audit Log
# ─────────────────────────────────────────────────

class AuditLog(Base):
    """
    Immutable record of every significant action in the system.

    Rules:
    - Never delete audit log records
    - Never update audit log records
    - organization_id is NULL for platform-level actions (Super Admin)
    - metadata stores before/after state, reason, and other context

    action examples:
    - 'organization.created'
    - 'organization.suspended'
    - 'user.invited'
    - 'subscription.plan_changed'
    - 'feature_override.enabled'
    """

    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=True,
    )
    actor_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[Optional[str]] = mapped_column(String(100))
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    action_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict, name='metadata')
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("idx_audit_logs_org_id", "organization_id"),
        Index("idx_audit_logs_actor", "actor_user_id"),
        Index("idx_audit_logs_created_at", "created_at"),
        Index("idx_audit_logs_action", "action"),
    )

    organization: Mapped[Optional["Organization"]] = relationship(
        "Organization", back_populates="audit_logs"
    )
    actor_user: Mapped[Optional["User"]] = relationship(
        "User", back_populates="audit_logs"
    )

    def __repr__(self) -> str:
        return f"<AuditLog action={self.action} actor={self.actor_user_id}>"


# ─────────────────────────────────────────────────
# Inventory Item
# ─────────────────────────────────────────────────

class InventoryItem(Base, TimestampMixin):
    """
    Jewellery Inventory Item tracking SKU, Metal, Purity, Net/Gross weight, fine weight, and making charges.
    """

    __tablename__ = "inventory_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    branch_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("branches.id", ondelete="SET NULL"),
        nullable=True,
    )
    sku: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, default="Ring")
    metal_type: Mapped[str] = mapped_column(String(50), nullable=False, default="Gold")
    purity: Mapped[str] = mapped_column(String(50), nullable=False, default="22K")
    purity_percentage: Mapped[float] = mapped_column(nullable=False, default=91.6)
    gross_weight: Mapped[float] = mapped_column(nullable=False, default=0.0)
    net_weight: Mapped[float] = mapped_column(nullable=False, default=0.0)
    fine_weight: Mapped[float] = mapped_column(nullable=False, default=0.0)
    stone_weight: Mapped[float] = mapped_column(nullable=False, default=0.0)
    making_charge_type: Mapped[str] = mapped_column(String(50), default="per_gram")
    making_charge_rate: Mapped[float] = mapped_column(nullable=False, default=0.0)
    quantity: Mapped[int] = mapped_column(nullable=False, default=1)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="in_stock")

    __table_args__ = (
        UniqueConstraint("organization_id", "sku", name="uq_org_inventory_sku"),
        Index("idx_inventory_org_id", "organization_id"),
        Index("idx_inventory_sku", "sku"),
        Index("idx_inventory_category", "category"),
    )

    organization: Mapped["Organization"] = relationship("Organization")
    branch: Mapped[Optional["Branch"]] = relationship("Branch")

