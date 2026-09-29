"""
Subscription Plan & Organization Entitlements Service.
"""

from datetime import datetime, timezone
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.exceptions import NotFoundError, ValidationError
from app.modules.subscriptions.schemas import (
    FeatureOverrideCreate,
    OrganizationSubscriptionCreate,
    SubscriptionPlanCreate,
    SubscriptionPlanUpdate,
)
from app.services.audit import log_audit_action
from app.shared.models import (
    Organization,
    OrganizationFeatureOverride,
    OrganizationSubscription,
    PlanFeature,
    SubscriptionPlan,
    User,
)


class SubscriptionService:
    def __init__(self, db: Session):
        self.db = db

    def create_plan(self, data: SubscriptionPlanCreate, actor: User) -> SubscriptionPlan:
        # Check duplicate plan name
        existing = (
            self.db.query(SubscriptionPlan)
            .filter(SubscriptionPlan.name == data.name)
            .first()
        )
        if existing:
            raise ValidationError(f"Plan with name '{data.name}' already exists")

        plan = SubscriptionPlan(
            name=data.name,
            description=data.description,
            price_monthly=data.price_monthly,
            price_yearly=data.price_yearly,
            currency=data.currency,
            status=data.status,
        )
        self.db.add(plan)
        self.db.flush()

        if data.features:
            for feat in data.features:
                pf = PlanFeature(
                    plan_id=plan.id,
                    feature_key=feat.feature_key,
                    enabled=feat.enabled,
                    limit_value=feat.limit_value,
                )
                self.db.add(pf)

        self.db.commit()
        self.db.refresh(plan)

        log_audit_action(
            db=self.db,
            action="subscription_plan.created",
            actor_user_id=actor.id,
            entity_type="subscription_plan",
            entity_id=plan.id,
            metadata={"plan_name": plan.name, "features_count": len(data.features or [])},
        )

        return plan

    def list_plans(self, status: Optional[str] = None) -> List[SubscriptionPlan]:
        query = self.db.query(SubscriptionPlan)
        if status:
            query = query.filter(SubscriptionPlan.status == status)
        return query.order_by(SubscriptionPlan.created_at.desc()).all()

    def get_plan(self, plan_id: UUID) -> SubscriptionPlan:
        plan = self.db.query(SubscriptionPlan).filter(SubscriptionPlan.id == plan_id).first()
        if not plan:
            raise NotFoundError("Subscription plan not found")
        return plan

    def update_plan(
        self, plan_id: UUID, data: SubscriptionPlanUpdate, actor: User
    ) -> SubscriptionPlan:
        plan = self.get_plan(plan_id)

        if data.name and data.name != plan.name:
            existing = (
                self.db.query(SubscriptionPlan)
                .filter(SubscriptionPlan.name == data.name, SubscriptionPlan.id != plan_id)
                .first()
            )
            if existing:
                raise ValidationError(f"Plan name '{data.name}' already taken")
            plan.name = data.name

        if data.description is not None:
            plan.description = data.description
        if data.price_monthly is not None:
            plan.price_monthly = data.price_monthly
        if data.price_yearly is not None:
            plan.price_yearly = data.price_yearly
        if data.status is not None:
            plan.status = data.status

        # Update features if provided
        if data.features is not None:
            # Delete existing features
            self.db.query(PlanFeature).filter(PlanFeature.plan_id == plan_id).delete()
            for feat in data.features:
                pf = PlanFeature(
                    plan_id=plan.id,
                    feature_key=feat.feature_key,
                    enabled=feat.enabled,
                    limit_value=feat.limit_value,
                )
                self.db.add(pf)

        self.db.commit()
        self.db.refresh(plan)

        log_audit_action(
            db=self.db,
            action="subscription_plan.updated",
            actor_user_id=actor.id,
            entity_type="subscription_plan",
            entity_id=plan.id,
            metadata={"plan_name": plan.name},
        )

        return plan

    def assign_organization_subscription(
        self, organization_id: UUID, data: OrganizationSubscriptionCreate, actor: User
    ) -> OrganizationSubscription:
        org = self.db.query(Organization).filter(Organization.id == organization_id).first()
        if not org:
            raise NotFoundError("Organization not found")

        plan = self.get_plan(data.plan_id)
        if plan.status != "active":
            raise ValidationError(f"Plan '{plan.name}' is not active")

        # Deactivate existing subscriptions
        existing_subs = (
            self.db.query(OrganizationSubscription)
            .filter(
                OrganizationSubscription.organization_id == organization_id,
                OrganizationSubscription.status.in_(["active", "trial"]),
            )
            .all()
        )
        for sub in existing_subs:
            sub.status = "expired"

        now = datetime.now(timezone.utc)
        starts_at = data.starts_at or now

        org_sub = OrganizationSubscription(
            organization_id=organization_id,
            plan_id=plan.id,
            status="active",
            starts_at=starts_at,
            ends_at=data.ends_at,
        )
        self.db.add(org_sub)
        self.db.commit()
        self.db.refresh(org_sub)

        log_audit_action(
            db=self.db,
            action="subscription.assigned",
            actor_user_id=actor.id,
            organization_id=organization_id,
            entity_type="organization_subscription",
            entity_id=org_sub.id,
            metadata={"plan_id": str(plan.id), "plan_name": plan.name},
        )

        return org_sub

    def get_organization_subscription(self, organization_id: UUID) -> Optional[OrganizationSubscription]:
        return (
            self.db.query(OrganizationSubscription)
            .filter(
                OrganizationSubscription.organization_id == organization_id,
                OrganizationSubscription.status.in_(["active", "trial"]),
            )
            .order_by(OrganizationSubscription.created_at.desc())
            .first()
        )

    def set_feature_override(
        self, organization_id: UUID, data: FeatureOverrideCreate, actor: User
    ) -> OrganizationFeatureOverride:
        org = self.db.query(Organization).filter(Organization.id == organization_id).first()
        if not org:
            raise NotFoundError("Organization not found")

        override = (
            self.db.query(OrganizationFeatureOverride)
            .filter(
                OrganizationFeatureOverride.organization_id == organization_id,
                OrganizationFeatureOverride.feature_key == data.feature_key,
            )
            .first()
        )

        if override:
            override.enabled = data.enabled
            override.limit_value = data.limit_value
            override.reason = data.reason
            override.created_by = actor.id
        else:
            override = OrganizationFeatureOverride(
                organization_id=organization_id,
                feature_key=data.feature_key,
                enabled=data.enabled,
                limit_value=data.limit_value,
                reason=data.reason,
                created_by=actor.id,
            )
            self.db.add(override)

        self.db.commit()
        self.db.refresh(override)

        log_audit_action(
            db=self.db,
            action="feature_override.set",
            actor_user_id=actor.id,
            organization_id=organization_id,
            entity_type="organization_feature_override",
            entity_id=override.id,
            metadata={
                "feature_key": data.feature_key,
                "enabled": data.enabled,
                "reason": data.reason,
            },
        )

        return override

    def get_organization_overrides(self, organization_id: UUID) -> List[OrganizationFeatureOverride]:
        return (
            self.db.query(OrganizationFeatureOverride)
            .filter(OrganizationFeatureOverride.organization_id == organization_id)
            .all()
        )
