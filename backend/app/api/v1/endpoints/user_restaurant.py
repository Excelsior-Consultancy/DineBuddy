from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.user_restaurant_service import UserRestaurantService
from app.schemas.user_restaurant_schema import UserRestaurantCreate,UserRestaurantResponse

router = APIRouter(
    prefix="/user-restaurants",
)

service = UserRestaurantService()

@router.post("/",response_model=UserRestaurantResponse,status_code=status.HTTP_201_CREATED,)
def assign_user_to_restaurant(
    payload: UserRestaurantCreate,
    db: Session = Depends(get_db),
):
    service.assign_user_to_restaurant(
        db=db,
        user_id=payload.user_id,
        restaurant_id=payload.restaurant_id,
    )

    return UserRestaurantResponse(
        status=True,
        message="User assigned to restaurant successfully",
    )
