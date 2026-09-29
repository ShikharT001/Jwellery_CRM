"""
Audit Log Schemas.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: Optional[UUID] = None
    actor_user_id: Optional[UUID] = None
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    action_metadata: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    created_at: datetime
