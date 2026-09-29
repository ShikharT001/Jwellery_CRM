"""
Roles and Permissions API Router.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.modules.roles.schemas import (
    MemberRoleAssignRequest,
    PermissionResponse,
    RoleCreate,
    RoleResponse,
    RoleUpdate,
)
from app.modules.roles.service import RoleService
from app.shared.models import User
from app.shared.schemas import APIResponse

router = APIRouter(tags=["Roles & Permissions"])


@router.get(
    "/permissions",
    response_model=APIResponse[List[PermissionResponse]],
    summary="List all platform permission keys",
)
def list_permissions(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = RoleService(db)
    permissions = service.list_permissions()
    return APIResponse(
        success=True,
        data=[PermissionResponse.model_validate(p) for p in permissions],
    )


@router.get(
    "/organizations/{organization_id}/roles",
    response_model=APIResponse[List[RoleResponse]],
    summary="List available roles for an organization",
)
def list_organization_roles(
    organization_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = RoleService(db)
    roles = service.list_organization_roles(organization_id)
    return APIResponse(
        success=True,
        data=[RoleResponse.model_validate(r) for r in roles],
    )


@router.post(
    "/organizations/{organization_id}/roles",
    response_model=APIResponse[RoleResponse],
    status_code=201,
    summary="Create custom organization role",
)
def create_organization_role(
    organization_id: UUID,
    data: RoleCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
):
    service = RoleService(db)
    role = service.create_custom_role(organization_id, data, actor)
    return APIResponse(
        success=True,
        message="Role created successfully",
        data=RoleResponse.model_validate(role),
    )


@router.patch(
    "/organizations/{organization_id}/roles/{role_id}",
    response_model=APIResponse[RoleResponse],
    summary="Update custom organization role",
)
def update_organization_role(
    organization_id: UUID,
    role_id: UUID,
    data: RoleUpdate,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
):
    service = RoleService(db)
    role = service.update_custom_role(organization_id, role_id, data, actor)
    return APIResponse(
        success=True,
        message="Role updated successfully",
        data=RoleResponse.model_validate(role),
    )


@router.post(
    "/organizations/{organization_id}/members/{member_id}/roles",
    response_model=APIResponse[List[RoleResponse]],
    summary="Assign roles to an organization member",
)
def assign_member_roles(
    organization_id: UUID,
    member_id: UUID,
    data: MemberRoleAssignRequest,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
):
    service = RoleService(db)
    assigned_roles = service.assign_member_roles(
        organization_id, member_id, data.role_ids, actor
    )
    return APIResponse(
        success=True,
        message="Member roles assigned successfully",
        data=[RoleResponse.model_validate(r) for r in assigned_roles],
    )
