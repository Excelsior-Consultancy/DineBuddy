from typing import Optional
from pydantic import BaseModel, Field
from decimal import Decimal

class MenuItemBase(BaseModel):
    category_id: int
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    price: Decimal = Field(..., ge=0, decimal_places=2)
    image_url: Optional[str] = None
    is_available: bool = True
    is_vegetarian: bool = False
    is_global: bool = False
    preparation_time_minutes: Optional[int] = None


class MenuItemCreate(MenuItemBase):
    restaurant_id: Optional[int] = None


class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Decimal | None = Field(None, ge=0, decimal_places=2)
    image_url: Optional[str] = None
    is_available: Optional[bool] = None
    is_vegetarian: Optional[bool] = None
    preparation_time_minutes: Optional[int] = None
    is_global: Optional[bool] = None
    restaurant_id: Optional[int] = None
    category_id: Optional[int] = None

class MenuItemRead(MenuItemBase):
    id: int
    restaurant_id: Optional[int]

    class Config:
        from_attributes = True
