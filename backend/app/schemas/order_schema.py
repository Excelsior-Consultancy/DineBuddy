from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal


class OrderItemCreate(BaseModel):
    menu_item_id: int
    variant_id: Optional[int] = None
    quantity: int = Field(..., gt=0)
    special_instructions: Optional[str] = None


class OrderCreate(BaseModel):
    table_number: Optional[str] = None
    items: List[OrderItemCreate]