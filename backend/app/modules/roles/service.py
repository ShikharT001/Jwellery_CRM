"""
Roles & Permissions Management Service.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.modules.roles.schemas import RoleCreate, RoleUpdate
from app.services.audit import log_audit_action
from app.shared.models import (
    MemberRole,
    OrganizationMember,
    Permission,
    Role,
    RolePermission,
    User,
)


class RoleService:
    def __init__(self, db: Session):
        self.db = db

    def list_permissions(self) -> List[Permission]:
        return self.db.query(Permission).order_by(Permission.module, Permission.key).all()

    def list_organization_roles(self, organization_id: UUID) -> List[Role]:
        """Returns both global system roles and custom organization roles."""
        roles = (
            self.db.query(Role)
            .filter(
                or_(
                    Role.is_system_role == True,
                    Role.organization_id == organization_id,
                )
            )
            .order_by(Role.is_system_role.desc(), Role.name)
            .all()
        )
        return roles

    def create_custom_role(
        self, organization_id: UUID, data: RoleCreate, actor: User
    ) -> Role:
        # Check duplicate role name for org
        existing = (
            self.db.query(Role)
            .filter(
                Role.organization_id == organization_id,
                Role.name == data.name,
            )
            .first()
        )
        if existing:
            raise ValidationError(f"Role '{data.name}' already exists in this organization")

        role = Role(
            organization_id=organization_id,
            name=data.name,
            description=data.description,
            is_system_role=False,
        )
        self.db.add(role)
        self.db.flush()

        if data.permission_ids:
            for pid in data.permission_ids:
                rp = RolePermission(role_id=role.id, permission_id=pid)
                self.db.add(rp)

        self.db.commit()
        self.db.refresh(role)

        log_audit_action(
            db=self.db,
            action="role.created",
            actor_user_id=actor.id,
            organization_id=organization_id,
            entity_type="role",
            entity_id=role.id,
            metadata={"role_name": role.name},
        )

        return role

    def update_custom_role(
        self, organization_id: UUID, role_id: UUID, data: RoleUpdate, actor: User
    ) -> Role:
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise NotFoundError("Role not found")
        if role.is_system_role:
            raise ForbiddenError("System roles cannot be modified")
        if role.organization_id != organization_id:
            raise ForbiddenError("Role does not belong to this organization")

        if data.name and data.name != role.name:
            role.name = data.name
        if data.description is not None:
            role.description = data.description

        if data.permission_ids is not None:
            self.db.query(RolePermission).filter(RolePermission.role_id == role_id).delete()
            for pid in data.permission_ids:
                rp = RolePermission(role_id=role.id, permission_id=pid)
                self.db.add(rp)

        self.db.commit()
        self.db.refresh(role)

        log_audit_action(
            db=self.db,
            action="role.updated",
            actor_user_id=actor.id,
            organization_id=organization_id,
            entity_type="role",
            entity_id=role.id,
            metadata={"role_name": role.name},
        )

        return role

    def assign_member_roles(
        self, organization_id: UUID, member_id: UUID, role_ids: List[UUID], actor: User
    ) -> List[Role]:
        member = (
            self.db.query(OrganizationMember)
            .filter(
                OrganizationMember.id == member_id,
                OrganizationMember.organization_id == organization_id,
            )
            .first()
        )
        if not member:
            raise NotFoundError("Organization member not found")

        # Validate that roles exist and belong to system or org
        roles = (
            self.db.query(Role)
            .filter(
                Role.id.in_(role_ids),
                or_(
                    Role.is_system_role == True,
                    Role.organization_id == organization_id,
                ),
            )
            .all()
        )
        if len(roles) != len(set(role_ids)):
            raise ValidationError("One or more invalid role IDs provided")

        # Clear existing member roles and re-assign
        self.db.query(MemberRole).filter(MemberRole.member_id == member_id).delete()

        for role in roles:
            mr = MemberRole(member_id=member.id, role_id=role.id)
            self.db.add(mr)

        self.db.commit()

        log_audit_action(
            db=self.db,
            action="member.roles_assigned",
            actor_user_id=actor.id,
            organization_id=organization_id,
            entity_type="organization_member",
            entity_id=member.id,
            metadata={"assigned_roles": [r.name for r in roles]},
        )

        return roles
