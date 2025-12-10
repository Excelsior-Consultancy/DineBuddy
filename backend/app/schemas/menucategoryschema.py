from pydantic import BaseModel
<<<<<<< HEAD

class MenuCategoryCreate(BaseModel):
=======
from typing import List, Optional

class MenuCategoryCreateRequest(BaseModel):
>>>>>>> excel-28-create-restaurant
    name: str
    restaurant_id: int

class MenuCategoryRead(BaseModel):
    id: int
    name: str
    restaurant_id: int

<<<<<<< HEAD
    class Config:
        orm_mode = True
=======

    class Config:
        from_attributes = True
>>>>>>> excel-28-create-restaurant
