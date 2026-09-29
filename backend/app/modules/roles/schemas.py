"""
Roles and Permissions Pydantic Schemas.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    key: str
    module: str
    description: Optional[str] = None


class RoleBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None


class RoleCreate(RoleBase):
    permission_ids: Optional[List[UUID]] = []


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permission_ids: Optional[List[UUID]] = None


class RoleResponse(RoleBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: Optional[UUID] = None
    is_system_role: bool
    created_at: datetime
    permissions: List[PermissionResponse] = []


class MemberRoleAssignRequest(BaseModel):
    role_ids: List[UUID]
