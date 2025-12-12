from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.restaurant_service import RestaurantService
from app.schemas.restaurant import RestaurantCreateRequest, RestaurantRead, RestaurantResponse, RestaurantListResponse, RestaurantDetailResponse
from app.core.database import get_db

router = APIRouter(prefix="/restaurants", tags=["restaurants"])


@router.post("/", response_model=RestaurantResponse)
def create_restaurant(restaurant: RestaurantCreateRequest, db: Session = Depends(get_db)):
    db_restaurant = RestaurantService().create(db, name=restaurant.name)
    return RestaurantResponse(
        status=True,
        message="Restaurant created successfully",
        data=RestaurantRead.model_validate(db_restaurant)
    )


@router.get("/", response_model=RestaurantListResponse)
def get_restaurants(db: Session = Depends(get_db)):
    restaurants = RestaurantService().get_all(db)

    return RestaurantListResponse(
        status=True,
        message="Restaurant list fetched",
        data=[RestaurantRead.model_validate(r) for r in restaurants]
    )


@router.get("/{restaurant_id}", response_model=RestaurantDetailResponse)
def get_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    db_restaurant = RestaurantService().get_by_id(db, restaurant_id)

    if not db_restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    return RestaurantDetailResponse(
        status=True,
        message="Restaurant fetched successfully",
        data=RestaurantRead.model_validate(db_restaurant)
    )
@router.delete("/{restaurant_id}", response_model=RestaurantDetailResponse)
def delete_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    if not RestaurantService().delete_by_id(db, restaurant_id):
        raise HTTPException(status_code=404, detail="Restaurant not found")

    return RestaurantDetailResponse(
        status=True,
        message="Restaurant deleted successfully",
        data=None
    )