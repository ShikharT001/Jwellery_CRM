"""
Organization repository — data access layer.

The repository pattern separates database query logic from business logic.
The service layer calls repository methods; the repository only interacts
with the database. This makes unit testing easier (mock the repository).
"""

from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.shared.models import Organization, Branch, OrganizationMember


class OrganizationRepository:
    """Data access methods for organizations and branches."""

    def __init__(self, db: Session):
        self.db = db

    # ─────────────────────────────────────────────
    # Organizations
    # ─────────────────────────────────────────────

    def create(self, **kwargs) -> Organization:
        """Create and persist a new organization."""
        org = Organization(**kwargs)
        self.db.add(org)
        self.db.flush()  # Get the ID without committing
        return org

    def get_by_id(self, org_id: UUID) -> Optional[Organization]:
        """Fetch an organization by its UUID."""
        return self.db.query(Organization).filter(Organization.id == org_id).first()

    def get_by_slug(self, slug: str) -> Optional[Organization]:
        """Fetch an organization by its slug (used for uniqueness checks)."""
        return self.db.query(Organization).filter(Organization.slug == slug).first()

    def list_all(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Organization], int]:
        """
        List all organizations with optional filtering and pagination.

        Returns:
            Tuple of (organizations list, total count)
        """
        query = self.db.query(Organization)

        if status:
            query = query.filter(Organization.status == status)

        if search:
            query = query.filter(
                Organization.name.ilike(f"%{search}%")
                | Organization.slug.ilike(f"%{search}%")
                | Organization.email.ilike(f"%{search}%")
            )

        total = query.count()
        organizations = (
            query.order_by(Organization.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return organizations, total

    def update(self, org: Organization, **kwargs) -> Organization:
        """Update organization fields."""
        for key, value in kwargs.items():
            if value is not None and hasattr(org, key):
                setattr(org, key, value)
        self.db.flush()
        return org

    def update_status(self, org: Organization, status: str) -> Organization:
        """Update organization status."""
        org.status = status
        self.db.flush()
        return org

    # ─────────────────────────────────────────────
    # Branches
    # ─────────────────────────────────────────────

    def create_branch(self, organization_id: UUID, **kwargs) -> Branch:
        """Create a branch for an organization."""
        branch = Branch(organization_id=organization_id, **kwargs)
        self.db.add(branch)
        self.db.flush()
        return branch

    def get_branch_by_id(self, branch_id: UUID) -> Optional[Branch]:
        """Fetch a branch by its UUID."""
        return self.db.query(Branch).filter(Branch.id == branch_id).first()

    def list_branches(
        self,
        organization_id: UUID,
        status: Optional[str] = None,
    ) -> List[Branch]:
        """List all branches for an organization."""
        query = self.db.query(Branch).filter(
            Branch.organization_id == organization_id
        )
        if status:
            query = query.filter(Branch.status == status)
        return query.order_by(Branch.name).all()

    def update_branch(self, branch: Branch, **kwargs) -> Branch:
        """Update branch fields."""
        for key, value in kwargs.items():
            if value is not None and hasattr(branch, key):
                setattr(branch, key, value)
        self.db.flush()
        return branch

    # ─────────────────────────────────────────────
    # Members
    # ─────────────────────────────────────────────

    def list_members(
        self, organization_id: UUID
    ) -> List[OrganizationMember]:
        """List all members of an organization."""
        return (
            self.db.query(OrganizationMember)
            .filter(OrganizationMember.organization_id == organization_id)
            .all()
        )

    def get_member(
        self, organization_id: UUID, user_id: UUID
    ) -> Optional[OrganizationMember]:
        """Get a specific member's record."""
        return (
            self.db.query(OrganizationMember)
            .filter(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.user_id == user_id,
            )
            .first()
        )
