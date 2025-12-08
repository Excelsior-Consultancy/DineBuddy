from pydantic import BaseModel
from typing import List, Optional

class RestaurantCreate(BaseModel):
    name: str

class RestaurantRead(BaseModel):
    id: int
    name: str
    categories: Optional[List["MenuCategoryRead"]] = []

    class Config:
        from_attributes = True

# Import after class definition to avoid circular import
from .menucategoryschema import MenuCategoryRead
RestaurantRead.model_rebuild()
