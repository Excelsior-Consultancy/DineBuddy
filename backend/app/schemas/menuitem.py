from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional

class MenuItemCreate(BaseModel):
    name: str = Field(..., description="The name of the menu item")
    description: Optional[str] = Field(None, description="Description of the menu item")
    price: Decimal = Field(..., gt=0, description="Price of the menu item (must be greater than 0)")
    menu_category_id: int = Field(..., description="The menu category this item belongs to")

class MenuItemRead(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: Decimal
    menu_category_id: int

    class Config:
        from_attributes = True

