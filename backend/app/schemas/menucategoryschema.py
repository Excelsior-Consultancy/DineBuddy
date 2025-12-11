from pydantic import BaseModel
from typing import List, Optional, Any


class MenuCategoryCreateRequest(BaseModel):
    name: str
    restaurant_id: int


class MenuCategoryRead(BaseModel):
    id: int
    name: str
    restaurant_id: int

    class Config:
        from_attributes = True


class GenericResponse(BaseModel):
    status: bool
    message: str
    data: Optional[Any] = None

class MenuCategoryResponse(BaseModel):
    status: bool
    message: str
    data: MenuCategoryRead

class MenuCategoryListResponse(BaseModel):
    status: bool
    message: str
    data: List[MenuCategoryRead]
