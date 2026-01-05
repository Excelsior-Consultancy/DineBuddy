from pydantic import BaseModel
from typing import Optional

class RestaurantSettingsRead(BaseModel):
    tax_percentage: Optional[float] = None
    service_charge: Optional[float] = None
    auto_accept_orders: bool
    order_preparation_time: Optional[int] = None

    class Config:
        from_attributes = True

class RestaurantRead(BaseModel):
    # existing fields...
    settings: Optional[RestaurantSettingsRead] = None
