from pydantic import BaseModel
from typing import List, Optional

class MenuCategoryCreateRequest(BaseModel):
    name: str
    restaurant_id: int

class MenuCategoryRead(BaseModel):
    id: int
    name: str
    restaurant_id: int


    class Config:
        from_attributes = True
