from pydantic import BaseModel
from typing import List, Optional

class MenuCategoryCreate(BaseModel):
    name: str
    restaurant_id: int

class MenuCategoryRead(BaseModel):
    id: int
    name: str
    restaurant_id: int
    menu_items: Optional[List["MenuItemRead"]] = []

    class Config:
        from_attributes = True

# Import after class definition to avoid circular import
from .menuitem import MenuItemRead
MenuCategoryRead.model_rebuild()