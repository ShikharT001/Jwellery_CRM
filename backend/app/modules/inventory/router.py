"""
Inventory Items API Router.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.modules.inventory.schemas import (
    InventoryItemCreate,
    InventoryItemResponse,
    InventoryItemUpdate,
)
from app.modules.inventory.service import InventoryService
from app.shared.models import User
from app.shared.schemas import APIResponse, PaginatedResponse

router = APIRouter(prefix="/organizations/{organization_id}/inventory", tags=["Inventory Management"])


@router.post(
    "",
    response_model=APIResponse[InventoryItemResponse],
    status_code=201,
    summary="Add new jewellery item to inventory",
)
def create_inventory_item(
    organization_id: UUID,
    data: InventoryItemCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(get_current_user),
):
    service = InventoryService(db)
    item = service.create_item(organization_id, data, actor)
    return APIResponse(
        success=True,
        message="Inventory item added successfully",
        data=InventoryItemResponse.model_validate(item),
    )


@router.get(
    "",
    response_model=PaginatedResponse[InventoryItemResponse],
    summary="List organization inventory items",
)
def list_inventory_items(
    organization_id: UUID,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    metal_type: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = InventoryService(db)
    items, total, total_pages = service.list_items(
        organization_id=organization_id,
        page=page,
        page_size=page_size,
        search=search,
        category=category,
        metal_type=metal_type,
    )
    return PaginatedResponse(
        success=True,
        data=[InventoryItemResponse.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/{item_id}",
    response_model=APIResponse[InventoryItemResponse],
    summary="Get single inventory item details",
)
def get_inventory_item(
    organization_id: UUID,
    item_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = InventoryService(db)
    item = service.get_item(organization_id, item_id)
    return APIResponse(
        success=True,
        data=InventoryItemResponse.model_validate(item),
    )
