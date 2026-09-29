"""
Alembic environment configuration.

This file is executed by Alembic when running migrations.
It:
1. Imports all models so Alembic can detect them
2. Connects to the database using our application settings
3. Configures the migration runner (online/offline modes)
"""

import sys
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Add the backend directory to the Python path
# This allows importing app modules from the migrations directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all models so Alembic detects schema changes
# This import MUST happen before Base.metadata is referenced
from app.shared.models import (  # noqa: F401
    User,
    Organization,
    Branch,
    OrganizationMember,
    Role,
    Permission,
    RolePermission,
    MemberRole,
    SubscriptionPlan,
    PlanFeature,
    OrganizationSubscription,
    OrganizationFeatureOverride,
    AuditLog,
)
from app.db.base import Base
from app.core.config import settings

# Alembic Config object (reads from alembic.ini)
config = context.config

# Override the database URL from our application settings
# This ensures migrations use the same database as the application
config.set_main_option("sqlalchemy.url", settings.database_url)

# Configure Python logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# The SQLAlchemy MetaData object for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    In offline mode, Alembic generates SQL scripts without connecting
    to the database. Useful for generating migration scripts for review.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    In online mode, Alembic connects to the database and applies
    migrations directly. This is the mode used in production.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # No pooling for migration connections
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
