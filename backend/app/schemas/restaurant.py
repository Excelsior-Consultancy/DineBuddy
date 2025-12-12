from pydantic import BaseModel
from typing import List, Optional


class RestaurantCreateRequest(BaseModel):
    name: str


class RestaurantRead(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True  # Pydantic v2 replacement for orm_mode
    }


class RestaurantResponse(BaseModel):
    status: bool
    message: str
    data: RestaurantRead


class RestaurantListResponse(BaseModel):
    status: bool
    message: str
    data: List[RestaurantRead]


class RestaurantDetailResponse(BaseModel):
    status: bool
    message: str
    data: Optional[RestaurantRead] = None
