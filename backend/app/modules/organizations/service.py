"""
Organization service — business logic layer.

The service layer orchestrates repository calls, business rule validation,
audit logging, and database transaction management.

Rules:
- Do NOT put business logic in route handlers
- Do NOT put database calls in route handlers
- Service methods are the only place that should call db.commit()
- Always audit log Super Admin actions
"""

import math
from typing import Optional, Tuple, List
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.core.logging import get_logger
from app.modules.organizations.repository import OrganizationRepository
from app.modules.organizations.schemas import (
    BranchCreate,
    BranchUpdate,
    OrganizationCreate,
    OrganizationUpdate,
)
from app.shared.models import AuditLog, Branch, Organization, User

logger = get_logger(__name__)


class OrganizationService:
    """Business logic for organization and branch management."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = OrganizationRepository(db)

    # ─────────────────────────────────────────────
    # Organizations
    # ─────────────────────────────────────────────

    def create_organization(
        self,
        data: OrganizationCreate,
        actor: User,
    ) -> Organization:
        """
        Create a new organization on the platform.

        Only Super Admins can create organizations.
        Validates slug uniqueness before creating.
        """
        # Check slug uniqueness
        existing = self.repo.get_by_slug(data.slug)
        if existing:
            raise ConflictError(
                f"An organization with slug '{data.slug}' already exists"
            )

        org = self.repo.create(
            name=data.name,
            legal_name=data.legal_name,
            slug=data.slug,
            email=data.email,
            phone=data.phone,
            country=data.country,
            currency=data.currency,
            status="active",
        )

        # Audit log
        self._audit(
            actor=actor,
            action="organization.created",
            entity_type="organization",
            entity_id=org.id,
            organization_id=org.id,
            metadata={"name": org.name, "slug": org.slug},
        )

        self.db.commit()
        self.db.refresh(org)

        logger.info("Organization created", org_id=str(org.id), slug=org.slug, actor=str(actor.id))
        return org

    def list_organizations(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Organization], int, int]:
        """
        List all organizations (Super Admin only).

        Returns: (organizations, total, total_pages)
        """
        organizations, total = self.repo.list_all(
            page=page, page_size=page_size, status=status, search=search
        )
        total_pages = math.ceil(total / page_size) if total > 0 else 1
        return organizations, total, total_pages

    def get_organization(self, org_id: UUID) -> Organization:
        """Fetch a single organization by ID."""
        org = self.repo.get_by_id(org_id)
        if not org:
            raise NotFoundError("Organization", str(org_id))
        return org

    def update_organization(
        self,
        org_id: UUID,
        data: OrganizationUpdate,
        actor: User,
    ) -> Organization:
        """Update organization details."""
        org = self.get_organization(org_id)

        update_data = data.model_dump(exclude_none=True)
        if not update_data:
            return org

        before = {k: getattr(org, k) for k in update_data}
        self.repo.update(org, **update_data)

        self._audit(
            actor=actor,
            action="organization.updated",
            entity_type="organization",
            entity_id=org.id,
            organization_id=org.id,
            metadata={"before": before, "after": update_data},
        )

        self.db.commit()
        self.db.refresh(org)
        return org

    def update_organization_status(
        self,
        org_id: UUID,
        status: str,
        reason: Optional[str],
        actor: User,
    ) -> Organization:
        """
        Change an organization's status (Super Admin only).

        This is the mechanism for suspending, activating, and deactivating
        organizations. Every status change is audit-logged.
        """
        org = self.get_organization(org_id)
        old_status = org.status

        if old_status == status:
            raise ValidationError(f"Organization is already '{status}'")

        self.repo.update_status(org, status)

        self._audit(
            actor=actor,
            action=f"organization.{status}",
            entity_type="organization",
            entity_id=org.id,
            organization_id=org.id,
            metadata={
                "previous_status": old_status,
                "new_status": status,
                "reason": reason,
            },
        )

        self.db.commit()
        self.db.refresh(org)

        logger.info(
            "Organization status changed",
            org_id=str(org.id),
            old_status=old_status,
            new_status=status,
            actor=str(actor.id),
        )
        return org

    # ─────────────────────────────────────────────
    # Branches
    # ─────────────────────────────────────────────

    def create_branch(
        self,
        organization_id: UUID,
        data: BranchCreate,
        actor: User,
    ) -> Branch:
        """Create a new branch for an organization."""
        # Verify the organization exists
        org = self.get_organization(organization_id)

        # Only one head office branch per organization
        if data.is_head_office:
            existing_head = (
                self.db.query(Branch)
                .filter(
                    Branch.organization_id == organization_id,
                    Branch.is_head_office == True,
                    Branch.status != "closed",
                )
                .first()
            )
            if existing_head:
                raise ConflictError(
                    f"Organization already has a head office: '{existing_head.name}'. "
                    "Update the existing head office first."
                )

        branch = self.repo.create_branch(
            organization_id=organization_id,
            name=data.name,
            address=data.address,
            city=data.city,
            state=data.state,
            postal_code=data.postal_code,
            phone=data.phone,
            is_head_office=data.is_head_office,
            status="active",
        )

        self._audit(
            actor=actor,
            action="branch.created",
            entity_type="branch",
            entity_id=branch.id,
            organization_id=organization_id,
            metadata={"name": branch.name},
        )

        self.db.commit()
        self.db.refresh(branch)
        return branch

    def list_branches(
        self,
        organization_id: UUID,
        status: Optional[str] = None,
    ) -> List[Branch]:
        """List all branches for an organization."""
        return self.repo.list_branches(organization_id, status)

    def get_branch(self, branch_id: UUID, organization_id: UUID) -> Branch:
        """Fetch a single branch, ensuring it belongs to the given organization."""
        branch = self.repo.get_branch_by_id(branch_id)
        if not branch or branch.organization_id != organization_id:
            raise NotFoundError("Branch", str(branch_id))
        return branch

    def update_branch(
        self,
        branch_id: UUID,
        organization_id: UUID,
        data: BranchUpdate,
        actor: User,
    ) -> Branch:
        """Update branch details."""
        branch = self.get_branch(branch_id, organization_id)
        update_data = data.model_dump(exclude_none=True)

        if not update_data:
            return branch

        self.repo.update_branch(branch, **update_data)

        self._audit(
            actor=actor,
            action="branch.updated",
            entity_type="branch",
            entity_id=branch.id,
            organization_id=organization_id,
            metadata={"updates": update_data},
        )

        self.db.commit()
        self.db.refresh(branch)
        return branch

    # ─────────────────────────────────────────────
    # Internal helpers
    # ─────────────────────────────────────────────

    def _audit(
        self,
        actor: User,
        action: str,
        entity_type: str,
        entity_id: UUID,
        organization_id: Optional[UUID] = None,
        metadata: Optional[dict] = None,
    ) -> None:
        """
        Create an audit log entry.

        Called internally by service methods — never by route handlers.
        The audit log is written in the same transaction as the main operation.
        """
        log_entry = AuditLog(
            organization_id=organization_id,
            actor_user_id=actor.id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            action_metadata=metadata or {},
        )
        self.db.add(log_entry)
