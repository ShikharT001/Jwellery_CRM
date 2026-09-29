"""
Inventory Item Service.
"""

import random
import string
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationError
from app.modules.inventory.schemas import InventoryItemCreate, InventoryItemUpdate
from app.services.audit import log_audit_action
from app.shared.models import InventoryItem, Organization, User


def generate_sku(category: str, metal: str) -> str:
    cat_prefix = (category[:3] if category else "JWL").upper()
    metal_prefix = (metal[:1] if metal else "G").upper()
    rand = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f"{cat_prefix}-{metal_prefix}-{rand}"


class InventoryService:
    def __init__(self, db: Session):
        self.db = db

    def create_item(
        self, organization_id: UUID, data: InventoryItemCreate, actor: User
    ) -> InventoryItem:
        org = self.db.query(Organization).filter(Organization.id == organization_id).first()
        if not org:
            raise NotFoundError("Organization not found")

        sku = data.sku or generate_sku(data.category, data.metal_type)

        # Calculate Fine Weight = Net Weight * (Purity % / 100)
        fine_weight = round(data.net_weight * (data.purity_percentage / 100.0), 3)

        item = InventoryItem(
            organization_id=organization_id,
            branch_id=data.branch_id,
            sku=sku,
            name=data.name,
            category=data.category,
            metal_type=data.metal_type,
            purity=data.purity,
            purity_percentage=data.purity_percentage,
            gross_weight=data.gross_weight,
            net_weight=data.net_weight,
            fine_weight=fine_weight,
            stone_weight=data.stone_weight,
            making_charge_type=data.making_charge_type,
            making_charge_rate=data.making_charge_rate,
            quantity=data.quantity,
            status=data.status,
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)

        log_audit_action(
            db=self.db,
            action="inventory_item.created",
            actor_user_id=actor.id,
            organization_id=organization_id,
            entity_type="inventory_item",
            entity_id=item.id,
            metadata={"sku": item.sku, "name": item.name, "gross_weight": item.gross_weight},
        )

        return item

    def list_items(
        self,
        organization_id: UUID,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        category: Optional[str] = None,
        metal_type: Optional[str] = None,
    ) -> Tuple[List[InventoryItem], int, int]:
        query = self.db.query(InventoryItem).filter(
            InventoryItem.organization_id == organization_id
        )

        if search:
            query = query.filter(
                (InventoryItem.name.ilike(f"%{search}%"))
                | (InventoryItem.sku.ilike(f"%{search}%"))
            )
        if category:
            query = query.filter(InventoryItem.category == category)
        if metal_type:
            query = query.filter(InventoryItem.metal_type == metal_type)

        total = query.count()
        total_pages = (total + page_size - 1) // page_size if total > 0 else 1

        items = (
            query.order_by(InventoryItem.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return items, total, total_pages

    def get_item(self, organization_id: UUID, item_id: UUID) -> InventoryItem:
        item = (
            self.db.query(InventoryItem)
            .filter(
                InventoryItem.id == item_id,
                InventoryItem.organization_id == organization_id,
            )
            .first()
        )
        if not item:
            raise NotFoundError("Inventory item not found")
        return item
