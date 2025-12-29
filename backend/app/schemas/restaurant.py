from pydantic import BaseModel
from typing import Optional, List, Dict


class RestaurantCreateRequest(BaseModel):
    name: str
    address: str
    phone: str
    email: str
    logo_url: Optional[str] = None
    timezone: Optional[str] = "Asia/Kolkata"
    currency: Optional[str] = "INR"

class RestaurantUpdateRequest(BaseModel):
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: Optional[bool] = None
    timezone: Optional[str] = None
    currency: Optional[str] = None


class RestaurantRead(BaseModel):
    id: int
    name: str
    slug: str
    address: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    logo_url: Optional[str]
    is_active: bool
    timezone: Optional[str]
    currency: Optional[str]

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
    meta: Dict[str, int]


class RestaurantDetailResponse(BaseModel):
    status: bool
    message: str
    data: Optional[RestaurantRead] = None
