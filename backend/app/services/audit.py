"""
Audit Logging Service.

Provides helper functions for recording immutable administrative and security audit
logs across the platform.
"""

from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy.orm import Session
from app.shared.models import AuditLog


def log_audit_action(
    db: Session,
    action: str,
    actor_user_id: Optional[UUID] = None,
    organization_id: Optional[UUID] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[UUID] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
) -> AuditLog:
    """
    Record an audit log entry in the database.

    Args:
        db: SQLAlchemy database session
        action: Dot-notation action key (e.g., 'organization.created', 'organization.suspended')
        actor_user_id: UUID of the user performing the action (NULL for system actions)
        organization_id: UUID of the target organization (NULL for platform-level actions)
        entity_type: Category of entity modified (e.g., 'organization', 'subscription_plan')
        entity_id: UUID of the affected entity
        metadata: Dictionary containing additional contextual information
        ip_address: Optional IP address of the request sender

    Returns:
        AuditLog: The created audit log model instance
    """
    audit_entry = AuditLog(
        action=action,
        actor_user_id=actor_user_id,
        organization_id=organization_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action_metadata=metadata or {},
        ip_address=ip_address,
    )
    db.add(audit_entry)
    db.commit()
    db.refresh(audit_entry)
    return audit_entry
