"""
Audit Log Query Router for Super Admin & Organization Owners.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_super_admin
from app.modules.audit.schemas import AuditLogResponse
from app.shared.models import AuditLog, User
from app.shared.schemas import PaginatedResponse

router = APIRouter(prefix="/admin/audit-logs", tags=["Audit Logs"])


@router.get(
    "",
    response_model=PaginatedResponse[AuditLogResponse],
    summary="List platform audit logs (Super Admin)",
)
def list_audit_logs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    organization_id: Optional[UUID] = Query(default=None),
    actor_user_id: Optional[UUID] = Query(default=None),
    action: Optional[str] = Query(default=None),
    entity_type: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_super_admin),
):
    query = db.query(AuditLog)

    if organization_id:
        query = query.filter(AuditLog.organization_id == organization_id)
    if actor_user_id:
        query = query.filter(AuditLog.actor_user_id == actor_user_id)
    if action:
        query = query.filter(AuditLog.action.ilike(f"%{action}%"))
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)

    total = query.count()
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    audit_logs = (
        query.order_by(AuditLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return PaginatedResponse(
        success=True,
        data=[AuditLogResponse.model_validate(log) for log in audit_logs],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )
