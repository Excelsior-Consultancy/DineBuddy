from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.order_schema import OrderCreate
from app.services.order_service import create_order
from app.core.dependencies import get_current_user, get_restaurant_by_id


router = APIRouter()


@router.post("/restaurants/{restaurant_id}/orders")
def place_order(
    payload: OrderCreate,
    restaurant=Depends(get_restaurant_by_id),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    order = create_order(
        db=db,
        restaurant_id=restaurant.id,
        payload=payload,
        current_user=current_user,
    )

    return {
        "message": "Order placed successfully",
        "order_id": order.id,
        "total": order.total_amount,
        "status": order.status,
    }