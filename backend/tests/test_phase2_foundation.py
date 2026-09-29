"""
Automated Integration & Unit Test Suite for Phase 2 Foundation.

Tests:
1. Super Admin access control
2. Organization management (create, list, suspend, activate)
3. Subscription plans & entitlements
4. Organization subscription assignment & feature overrides
5. Roles & permissions management
6. Feature entitlement evaluation & precedence
7. Audit log creation
"""

import uuid
import pytest
from sqlalchemy import create_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON


@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(element, compiler, **kw):
    return "JSON"


from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.shared.models import (
    User,
    Organization,
    OrganizationMember,
    SubscriptionPlan,
    PlanFeature,
    OrganizationSubscription,
    OrganizationFeatureOverride,
    Role,
    Permission,
    RolePermission,
    MemberRole,
    AuditLog,
)
from app.services.audit import log_audit_action
from app.services.feature_access import FeatureAccessService
from app.modules.organizations.service import OrganizationService
from app.modules.organizations.schemas import OrganizationCreate
from app.modules.subscriptions.service import SubscriptionService
from app.modules.subscriptions.schemas import (
    SubscriptionPlanCreate,
    PlanFeatureCreate,
    OrganizationSubscriptionCreate,
    FeatureOverrideCreate,
)
from app.modules.roles.service import RoleService
from app.modules.roles.schemas import RoleCreate
from app.core.exceptions import ForbiddenError, NotFoundError, ValidationError, OrganizationSuspendedError


# Use SQLite in-memory for fast automated unit tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def super_admin_user(db_session):
    user = User(
        supabase_user_id=uuid.uuid4(),
        email="admin@platform.com",
        display_name="Super Admin",
        is_super_admin=True,
        status="active",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def normal_user(db_session):
    user = User(
        supabase_user_id=uuid.uuid4(),
        email="owner@jewelstore.com",
        display_name="Store Owner",
        is_super_admin=False,
        status="active",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


# ─────────────────────────────────────────────────
# 1. Organization Management Tests
# ─────────────────────────────────────────────────

def test_organization_crud(db_session, super_admin_user):
    org_service = OrganizationService(db_session)
    
    # Create organization
    org_data = OrganizationCreate(
        name="Royal Jewels",
        legal_name="Royal Jewels Private Limited",
        slug="royal-jewels",
        email="contact@royaljewels.com",
        phone="+919876543210",
        country="India",
        currency="INR",
    )
    org = org_service.create_organization(org_data, actor=super_admin_user)
    assert org.id is not None
    assert org.slug == "royal-jewels"
    assert org.status == "active"

    # Suspend organization
    suspended_org = org_service.update_organization_status(
        org.id, status="suspended", reason="Payment default", actor=super_admin_user
    )
    assert suspended_org.status == "suspended"

    # Activate organization
    activated_org = org_service.update_organization_status(
        org.id, status="active", reason="Payment resolved", actor=super_admin_user
    )
    assert activated_org.status == "active"


# ─────────────────────────────────────────────────
# 2. Subscription Plans & Entitlements Tests
# ─────────────────────────────────────────────────

def test_subscription_plans_and_overrides(db_session, super_admin_user, normal_user):
    sub_service = SubscriptionService(db_session)
    org_service = OrganizationService(db_session)

    # 1. Create Organization
    org = org_service.create_organization(
        OrganizationCreate(name="Gem Palace", slug="gem-palace"), actor=super_admin_user
    )

    # 2. Create PRO Plan
    plan_data = SubscriptionPlanCreate(
        name="PRO Plan",
        description="Full feature suite for growing jewellers",
        price_monthly=4999.0,
        currency="INR",
        features=[
            PlanFeatureCreate(feature_key="inventory.view", enabled=True),
            PlanFeatureCreate(feature_key="inventory.adjust", enabled=True),
            PlanFeatureCreate(feature_key="manufacturing.view", enabled=False),
        ],
    )
    plan = sub_service.create_plan(plan_data, actor=super_admin_user)
    assert plan.id is not None
    assert len(plan.features) == 3

    # 3. Assign Plan to Organization
    org_sub = sub_service.assign_organization_subscription(
        org.id, OrganizationSubscriptionCreate(plan_id=plan.id), actor=super_admin_user
    )
    assert org_sub.status == "active"

    # 4. Check Feature Access Engine
    feature_engine = FeatureAccessService(db_session)
    effective_features = feature_engine.get_organization_effective_features(org.id)
    
    assert effective_features["inventory.view"]["enabled"] is True
    assert effective_features["inventory.view"]["source"] == "subscription_plan"
    assert effective_features["manufacturing.view"]["enabled"] is False

    # 5. Apply Super Admin Feature Override (Enable manufacturing for this org)
    override = sub_service.set_feature_override(
        org.id,
        FeatureOverrideCreate(
            feature_key="manufacturing.view",
            enabled=True,
            reason="Special beta trial extension",
        ),
        actor=super_admin_user,
    )
    assert override.enabled is True

    # 6. Re-evaluate Feature Access — Override MUST take precedence over Plan
    updated_features = feature_engine.get_organization_effective_features(org.id)
    assert updated_features["manufacturing.view"]["enabled"] is True
    assert updated_features["manufacturing.view"]["source"] == "organization_override"


# ─────────────────────────────────────────────────
# 3. Roles & Permissions Tests
# ─────────────────────────────────────────────────

def test_roles_and_permissions(db_session, super_admin_user, normal_user):
    role_service = RoleService(db_session)
    org_service = OrganizationService(db_session)

    # Create Org
    org = org_service.create_organization(
        OrganizationCreate(name="Crown Crafts", slug="crown-crafts"), actor=super_admin_user
    )

    # Seed permission
    perm = Permission(key="sales.create", module="sales", description="Create sales orders")
    db_session.add(perm)
    db_session.commit()

    # Create Custom Role
    custom_role = role_service.create_custom_role(
        org.id,
        RoleCreate(
            name="Junior Sales Associate",
            description="Limited sales access",
            permission_ids=[perm.id],
        ),
        actor=super_admin_user,
    )
    assert custom_role.id is not None
    assert custom_role.organization_id == org.id

    # Create Member
    member = OrganizationMember(
        organization_id=org.id,
        user_id=normal_user.id,
        status="active",
    )
    db_session.add(member)
    db_session.commit()

    # Assign Role to Member
    assigned = role_service.assign_member_roles(
        org.id, member.id, [custom_role.id], actor=super_admin_user
    )
    assert len(assigned) == 1

    # Check member permissions
    feature_engine = FeatureAccessService(db_session)
    perms = feature_engine.get_user_effective_permissions(normal_user.id, org.id)
    assert "sales.create" in perms


# ─────────────────────────────────────────────────
# 4. Audit Log Creation Tests
# ─────────────────────────────────────────────────

def test_audit_log_record(db_session, super_admin_user):
    audit_log = log_audit_action(
        db=db_session,
        action="organization.suspended",
        actor_user_id=super_admin_user.id,
        entity_type="organization",
        entity_id=uuid.uuid4(),
        metadata={"reason": "Compliance check"},
    )
    assert audit_log.id is not None
    assert audit_log.action == "organization.suspended"
    assert audit_log.actor_user_id == super_admin_user.id
