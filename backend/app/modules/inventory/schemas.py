"""
Inventory Module Pydantic Schemas.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class InventoryItemBase(BaseModel):
    name: str = Field(..., max_length=255, example="22K Gold Diamond Engagement Ring")
    sku: Optional[str] = Field(default=None, max_length=100)
    category: str = Field(default="Ring", example="Ring")
    metal_type: str = Field(default="Gold", example="Gold")
    purity: str = Field(default="22K", example="22K")
    purity_percentage: float = Field(default=91.6, ge=0.0, le=100.0)
    gross_weight: float = Field(default=0.0, ge=0.0)
    net_weight: float = Field(default=0.0, ge=0.0)
    stone_weight: float = Field(default=0.0, ge=0.0)
    making_charge_type: str = Field(default="per_gram")
    making_charge_rate: float = Field(default=0.0, ge=0.0)
    quantity: int = Field(default=1, ge=1)
    status: str = Field(default="in_stock")
    branch_id: Optional[UUID] = None


class InventoryItemCreate(InventoryItemBase):
    pass


class InventoryItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    metal_type: Optional[str] = None
    purity: Optional[str] = None
    purity_percentage: Optional[float] = None
    gross_weight: Optional[float] = None
    net_weight: Optional[float] = None
    stone_weight: Optional[float] = None
    making_charge_type: Optional[str] = None
    making_charge_rate: Optional[float] = None
    quantity: Optional[int] = None
    status: Optional[str] = None
    branch_id: Optional[UUID] = None


class InventoryItemResponse(InventoryItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    fine_weight: float
    created_at: datetime
    updated_at: datetime
