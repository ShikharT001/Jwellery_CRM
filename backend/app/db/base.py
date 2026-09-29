"""
SQLAlchemy declarative base and shared model mixins.

The TimestampMixin adds created_at and updated_at columns to any model
that inherits from it, ensuring consistent auditing across all tables.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    SQLAlchemy declarative base.

    All ORM models must inherit from this class.
    Alembic's env.py imports this to detect schema changes.
    """
    pass


class TimestampMixin:
    """
    Adds created_at and updated_at columns to a model.

    - created_at: Set once when the row is inserted (server_default)
    - updated_at: Updated automatically on every row update (onupdate)

    Both columns use timezone-aware timestamps (TIMESTAMPTZ in PostgreSQL).
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
