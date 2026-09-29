"""
Organization API router.

Endpoints:
  Super Admin (platform-level):
    POST   /api/v1/organizations                    - Create organization
    GET    /api/v1/organizations                    - List all organizations
    GET    /api/v1/organizations/{id}               - Get organization details
    PATCH  /api/v1/organizations/{id}               - Update organization
    PATCH  /api/v1/organizations/{id}/status        - Change status (suspend/activate)

  Organization-level (authenticated member):
    GET    /api/v1/organizations/{id}/branches      - List branches
    POST   /api/v1/organizations/{id}/branches      - Create branch
    PATCH  /api/v1/organizations/{id}/branches/{bid} - Update branch
    GET    /api/v1/organizations/{id}/members       - List members
"""

import math
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.dependencies.auth import get_current_super_admin, get_current_user
from app.modules.organizations.schemas import (
    BranchCreate,
    BranchResponse,
    BranchUpdate,
    MemberResponse,
    OrganizationCreate,
    OrganizationListResponse,
    OrganizationResponse,
    OrganizationStatusUpdate,
    OrganizationUpdate,
)
from app.modules.organizations.service import OrganizationService
from app.shared.models import User
from app.shared.schemas import APIResponse, PaginatedResponse

router = APIRouter(prefix="/organizations", tags=["Organizations"])


# ─────────────────────────────────────────────────
# Super Admin Endpoints
# ─────────────────────────────────────────────────

@router.post(
    "",
    response_model=APIResponse[OrganizationResponse],
    status_code=201,
    summary="Create a new organization (Super Admin)",
)
def create_organization(
    data: OrganizationCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_super_admin),
):
    """
    Create a new jewellery store organization on the platform.

    **Requires:** Super Admin
    """
    service = OrganizationService(db)
    org = service.create_organization(data, actor)
    return APIResponse(
        success=True,
        message="Organization created successfully",
        data=OrganizationResponse.model_validate(org),
    )


@router.get(
    "",
    response_model=PaginatedResponse[OrganizationListResponse],
    summary="List all organizations (Super Admin)",
)
def list_organizations(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_super_admin),
):
    """
    List all organizations on the platform with pagination and filtering.

    **Requires:** Super Admin
    """
    service = OrganizationService(db)
    orgs, total, total_pages = service.list_organizations(
        page=page, page_size=page_size, status=status, search=search
    )
    return PaginatedResponse(
        success=True,
        data=[OrganizationListResponse.model_validate(o) for o in orgs],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/{organization_id}",
    response_model=APIResponse[OrganizationResponse],
    summary="Get organization details",
)
def get_organization(
    organization_id: UUID,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_super_admin),
):
    """
    Get detailed information about a specific organization.

    **Requires:** Super Admin
    """
    service = OrganizationService(db)
    org = service.get_organization(organization_id)
    return APIResponse(
        success=True,
        data=OrganizationResponse.model_validate(org),
    )


@router.patch(
    "/{organization_id}",
    response_model=APIResponse[OrganizationResponse],
    summary="Update organization details",
)
def update_organization(
    organization_id: UUID,
    data: OrganizationUpdate,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_super_admin),
):
    """
    Update organization details (name, contact info, etc.).

    **Requires:** Super Admin
    """
    service = OrganizationService(db)
    org = service.update_organization(organization_id, data, actor)
    return APIResponse(
        success=True,
        message="Organization updated successfully",
        data=OrganizationResponse.model_validate(org),
    )


@router.patch(
    "/{organization_id}/status",
    response_model=APIResponse[OrganizationResponse],
    summary="Change organization status (Super Admin)",
)
def update_organization_status(
    organization_id: UUID,
    data: OrganizationStatusUpdate,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_super_admin),
):
    """
    Suspend, activate, or deactivate an organization.

    Every status change is recorded in the audit log.

    **Requires:** Super Admin
    """
    service = OrganizationService(db)
    org = service.update_organization_status(
        organization_id, data.status, data.reason, actor
    )
    return APIResponse(
        success=True,
        message=f"Organization status changed to '{data.status}'",
        data=OrganizationResponse.model_validate(org),
    )


# ─────────────────────────────────────────────────
# Branch Endpoints
# ─────────────────────────────────────────────────

@router.post(
    "/{organization_id}/branches",
    response_model=APIResponse[BranchResponse],
    status_code=201,
    summary="Create a branch",
)
def create_branch(
    organization_id: UUID,
    data: BranchCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
):
    """
    Create a new branch for an organization.

    **Requires:** Organization Owner or Super Admin
    """
    service = OrganizationService(db)
    branch = service.create_branch(organization_id, data, actor)
    return APIResponse(
        success=True,
        message="Branch created successfully",
        data=BranchResponse.model_validate(branch),
    )


@router.get(
    "/{organization_id}/branches",
    response_model=APIResponse[List[BranchResponse]],
    summary="List branches",
)
def list_branches(
    organization_id: UUID,
    status: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
):
    """
    List all branches for an organization.

    **Requires:** Authenticated member of the organization
    """
    service = OrganizationService(db)
    branches = service.list_branches(organization_id, status)
    return APIResponse(
        success=True,
        data=[BranchResponse.model_validate(b) for b in branches],
    )


@router.patch(
    "/{organization_id}/branches/{branch_id}",
    response_model=APIResponse[BranchResponse],
    summary="Update a branch",
)
def update_branch(
    organization_id: UUID,
    branch_id: UUID,
    data: BranchUpdate,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
):
    """
    Update branch details.

    **Requires:** Branch Manager or higher
    """
    service = OrganizationService(db)
    branch = service.update_branch(branch_id, organization_id, data, actor)
    return APIResponse(
        success=True,
        message="Branch updated successfully",
        data=BranchResponse.model_validate(branch),
    )
