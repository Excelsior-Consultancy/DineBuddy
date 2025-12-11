from pydantic import BaseModel
from typing import List, Optional

class RestaurantCreateRequest(BaseModel):
    name: str


class RestaurantRead(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class RestaurantResponse(BaseModel):
    status: bool
    message: str
    data: RestaurantRead


class RestaurantListResponse(BaseModel):
    status: bool
    message: str
    data: List[RestaurantRead]


class GenericResponse(BaseModel):
    status: bool
    message: str
    data: Optional[RestaurantRead] = None

# Import after class definition to avoid circular import
