"""Initial platform schema

Creates all core platform tables:
- users
- organizations
- branches
- organization_members
- roles
- permissions
- role_permissions
- member_roles
- subscription_plans
- plan_features
- organization_subscriptions
- organization_feature_overrides
- audit_logs

Also seeds:
- System roles (ORGANIZATION_OWNER, BRANCH_MANAGER, etc.)
- Platform permissions (inventory.view, sales.create, etc.)
- Default role-permission mappings

Revision ID: 001
Revises: None
Create Date: 2026-09-17
"""

from typing import Sequence, Union
import uuid
from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET

# revision identifiers
revision: str = "001_initial_platform_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ─────────────────────────────────────────────
    # Enable UUID extension (required for gen_random_uuid())
    # ─────────────────────────────────────────────
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    # ─────────────────────────────────────────────
    # users
    # ─────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("supabase_user_id", UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column("display_name", sa.String(255), nullable=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("is_super_admin", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint("status IN ('active', 'suspended', 'deactivated')", name="ck_users_status"),
    )
    op.create_index("idx_users_supabase_user_id", "users", ["supabase_user_id"], unique=True)
    op.create_index("idx_users_email", "users", ["email"], unique=True)

    # ─────────────────────────────────────────────
    # organizations
    # ─────────────────────────────────────────────
    op.create_table(
        "organizations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("legal_name", sa.String(255), nullable=True),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("country", sa.String(100), nullable=False, server_default="India"),
        sa.Column("currency", sa.String(10), nullable=False, server_default="INR"),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("settings", JSONB, nullable=True, server_default="'{}'::jsonb"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint(
            "status IN ('active', 'trial', 'suspended', 'inactive')",
            name="ck_organizations_status",
        ),
    )
    op.create_index("idx_organizations_slug", "organizations", ["slug"], unique=True)
    op.create_index("idx_organizations_status", "organizations", ["status"])

    # ─────────────────────────────────────────────
    # branches
    # ─────────────────────────────────────────────
    op.create_table(
        "branches",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("state", sa.String(100), nullable=True),
        sa.Column("postal_code", sa.String(20), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("is_head_office", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint(
            "status IN ('active', 'inactive', 'closed')",
            name="ck_branches_status",
        ),
    )
    op.create_index("idx_branches_organization_id", "branches", ["organization_id"])
    op.create_index("idx_branches_status", "branches", ["organization_id", "status"])

    # ─────────────────────────────────────────────
    # organization_members
    # ─────────────────────────────────────────────
    op.create_table(
        "organization_members",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("NOW()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint(
            "status IN ('active', 'suspended', 'invited', 'deactivated')",
            name="ck_org_members_status",
        ),
        sa.UniqueConstraint("organization_id", "user_id", name="uq_org_member"),
    )
    op.create_index("idx_org_members_user_id", "organization_members", ["user_id"])
    op.create_index("idx_org_members_org_id", "organization_members", ["organization_id"])

    # ─────────────────────────────────────────────
    # roles
    # ─────────────────────────────────────────────
    op.create_table(
        "roles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_system_role", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("organization_id", "name", name="uq_role_name_per_org"),
    )
    op.create_index("idx_roles_organization_id", "roles", ["organization_id"])

    # ─────────────────────────────────────────────
    # permissions
    # ─────────────────────────────────────────────
    op.create_table(
        "permissions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("key", sa.String(100), nullable=False, unique=True),
        sa.Column("module", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("idx_permissions_key", "permissions", ["key"], unique=True)
    op.create_index("idx_permissions_module", "permissions", ["module"])

    # ─────────────────────────────────────────────
    # role_permissions
    # ─────────────────────────────────────────────
    op.create_table(
        "role_permissions",
        sa.Column("role_id", UUID(as_uuid=True), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("permission_id", UUID(as_uuid=True), sa.ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
    )
    op.create_index("idx_role_permissions_role_id", "role_permissions", ["role_id"])

    # ─────────────────────────────────────────────
    # member_roles
    # ─────────────────────────────────────────────
    op.create_table(
        "member_roles",
        sa.Column("member_id", UUID(as_uuid=True), sa.ForeignKey("organization_members.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("role_id", UUID(as_uuid=True), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    )
    op.create_index("idx_member_roles_member_id", "member_roles", ["member_id"])

    # ─────────────────────────────────────────────
    # subscription_plans
    # ─────────────────────────────────────────────
    op.create_table(
        "subscription_plans",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price_monthly", sa.Numeric(10, 2), nullable=True),
        sa.Column("price_yearly", sa.Numeric(10, 2), nullable=True),
        sa.Column("currency", sa.String(10), nullable=False, server_default="INR"),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint(
            "status IN ('active', 'inactive', 'deprecated')",
            name="ck_subscription_plans_status",
        ),
    )

    # ─────────────────────────────────────────────
    # plan_features
    # ─────────────────────────────────────────────
    op.create_table(
        "plan_features",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("plan_id", UUID(as_uuid=True), sa.ForeignKey("subscription_plans.id", ondelete="CASCADE"), nullable=False),
        sa.Column("feature_key", sa.String(100), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("limit_value", sa.Integer(), nullable=True),
        sa.UniqueConstraint("plan_id", "feature_key", name="uq_plan_feature"),
    )
    op.create_index("idx_plan_features_plan_id", "plan_features", ["plan_id"])

    # ─────────────────────────────────────────────
    # organization_subscriptions
    # ─────────────────────────────────────────────
    op.create_table(
        "organization_subscriptions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("plan_id", UUID(as_uuid=True), sa.ForeignKey("subscription_plans.id"), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint(
            "status IN ('active', 'expired', 'cancelled', 'trial')",
            name="ck_org_subscriptions_status",
        ),
    )
    op.create_index("idx_org_subscriptions_org_id", "organization_subscriptions", ["organization_id"])

    # ─────────────────────────────────────────────
    # organization_feature_overrides
    # ─────────────────────────────────────────────
    op.create_table(
        "organization_feature_overrides",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("feature_key", sa.String(100), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("limit_value", sa.Integer(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("organization_id", "feature_key", name="uq_org_feature_override"),
    )
    op.create_index("idx_feature_overrides_org_id", "organization_feature_overrides", ["organization_id"])

    # ─────────────────────────────────────────────
    # audit_logs
    # ─────────────────────────────────────────────
    op.create_table(
        "audit_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=True),
        sa.Column("actor_user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=True),
        sa.Column("entity_id", UUID(as_uuid=True), nullable=True),
        sa.Column("metadata", JSONB, nullable=True, server_default="'{}'::jsonb"),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("idx_audit_logs_org_id", "audit_logs", ["organization_id"])
    op.create_index("idx_audit_logs_actor", "audit_logs", ["actor_user_id"])
    op.create_index("idx_audit_logs_created_at", "audit_logs", ["created_at"])
    op.create_index("idx_audit_logs_action", "audit_logs", ["action"])

    # ─────────────────────────────────────────────
    # updated_at trigger function (auto-update on row update)
    # ─────────────────────────────────────────────
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)

    for table in ["users", "organizations", "branches", "subscription_plans", "organization_subscriptions", "organization_feature_overrides"]:
        op.execute(f"""
            CREATE TRIGGER trigger_update_{table}_updated_at
            BEFORE UPDATE ON {table}
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """)

    # ─────────────────────────────────────────────
    # SEED: System Roles
    # ─────────────────────────────────────────────
    now = datetime.now(timezone.utc).isoformat()

    system_roles = [
        {
            "id": str(uuid.uuid4()),
            "name": "ORGANIZATION_OWNER",
            "description": "Full access to all organization features",
            "is_system_role": True,
            "created_at": now,
        },
        {
            "id": str(uuid.uuid4()),
            "name": "BRANCH_MANAGER",
            "description": "Manages a specific branch — staff, inventory, operations",
            "is_system_role": True,
            "created_at": now,
        },
        {
            "id": str(uuid.uuid4()),
            "name": "SALES_STAFF",
            "description": "Access to POS, customer management, and sales",
            "is_system_role": True,
            "created_at": now,
        },
        {
            "id": str(uuid.uuid4()),
            "name": "INVENTORY_MANAGER",
            "description": "Access to inventory management and stock movements",
            "is_system_role": True,
            "created_at": now,
        },
        {
            "id": str(uuid.uuid4()),
            "name": "ACCOUNTANT",
            "description": "Access to financial reports and accounting workflows",
            "is_system_role": True,
            "created_at": now,
        },
        {
            "id": str(uuid.uuid4()),
            "name": "WORKSHOP_MANAGER",
            "description": "Access to manufacturing, repair, and job work operations",
            "is_system_role": True,
            "created_at": now,
        },
    ]

    op.bulk_insert(
        sa.table(
            "roles",
            sa.column("id", UUID(as_uuid=True)),
            sa.column("organization_id", UUID(as_uuid=True)),
            sa.column("name", sa.String),
            sa.column("description", sa.Text),
            sa.column("is_system_role", sa.Boolean),
            sa.column("created_at", sa.DateTime(timezone=True)),
        ),
        [
            {
                "id": r["id"],
                "organization_id": None,
                "name": r["name"],
                "description": r["description"],
                "is_system_role": r["is_system_role"],
                "created_at": r["created_at"],
            }
            for r in system_roles
        ],
    )

    # ─────────────────────────────────────────────
    # SEED: Platform Permissions
    # ─────────────────────────────────────────────
    permissions = [
        # Inventory
        ("inventory.view", "inventory", "View inventory items"),
        ("inventory.create", "inventory", "Create inventory items"),
        ("inventory.update", "inventory", "Update inventory items"),
        ("inventory.delete", "inventory", "Delete inventory items"),
        ("inventory.adjust", "inventory", "Make stock adjustments"),
        ("inventory.transfer", "inventory", "Transfer stock between branches"),
        ("inventory.reports", "inventory", "View inventory reports"),
        # Sales & Billing
        ("sales.view", "sales", "View sales records"),
        ("sales.create", "sales", "Create sales"),
        ("invoices.create", "sales", "Create invoices"),
        ("invoices.view", "sales", "View invoices"),
        ("sales.returns", "sales", "Process returns"),
        ("payments.record", "sales", "Record payments"),
        # Customers
        ("customers.view", "customers", "View customer records"),
        ("customers.create", "customers", "Create customers"),
        ("customers.update", "customers", "Update customers"),
        ("customers.delete", "customers", "Delete customers"),
        ("enquiries.manage", "customers", "Manage customer enquiries"),
        ("followups.manage", "customers", "Manage follow-ups"),
        # Purchases
        ("purchases.view", "purchases", "View purchase records"),
        ("purchases.create", "purchases", "Create purchase orders"),
        ("purchases.receive", "purchases", "Mark purchases as received"),
        ("suppliers.manage", "purchases", "Manage suppliers"),
        # Manufacturing
        ("manufacturing.view", "manufacturing", "View manufacturing orders"),
        ("manufacturing.create", "manufacturing", "Create manufacturing orders"),
        ("manufacturing.update", "manufacturing", "Update manufacturing orders"),
        ("manufacturing.orders.manage", "manufacturing", "Full manufacturing order management"),
        # Reports
        ("reports.sales", "reports", "View sales reports"),
        ("reports.inventory", "reports", "View inventory reports"),
        ("reports.purchase", "reports", "View purchase reports"),
        ("reports.financial", "reports", "View financial reports"),
        # Admin
        ("branches.manage", "admin", "Manage branches"),
        ("users.manage", "admin", "Manage organization users"),
        ("settings.manage", "admin", "Manage organization settings"),
    ]

    op.bulk_insert(
        sa.table(
            "permissions",
            sa.column("id", UUID(as_uuid=True)),
            sa.column("key", sa.String),
            sa.column("module", sa.String),
            sa.column("description", sa.Text),
            sa.column("created_at", sa.DateTime(timezone=True)),
        ),
        [
            {
                "id": str(uuid.uuid4()),
                "key": key,
                "module": module,
                "description": description,
                "created_at": now,
            }
            for key, module, description in permissions
        ],
    )


def downgrade() -> None:
    """Drop all tables in reverse dependency order."""
    # Drop triggers first
    for table in ["users", "organizations", "branches", "subscription_plans", "organization_subscriptions", "organization_feature_overrides"]:
        op.execute(f"DROP TRIGGER IF EXISTS trigger_update_{table}_updated_at ON {table}")

    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")

    op.drop_table("audit_logs")
    op.drop_table("organization_feature_overrides")
    op.drop_table("organization_subscriptions")
    op.drop_table("plan_features")
    op.drop_table("subscription_plans")
    op.drop_table("member_roles")
    op.drop_table("role_permissions")
    op.drop_table("permissions")
    op.drop_table("roles")
    op.drop_table("organization_members")
    op.drop_table("branches")
    op.drop_table("organizations")
    op.drop_table("users")
