from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.services.restaurant_service import RestaurantService
from app.schemas.restaurant import RestaurantCreateRequest, RestaurantRead, RestaurantResponse, RestaurantListResponse, GenericResponse
from app.core.database import get_db
from app.models.restaurant import Restaurant

router = APIRouter(prefix="/restaurants", tags=["restaurants"])

# ------ Endpoints ------ #
@router.post("/create", response_model=RestaurantRead)
def create_restaurant(restaurant: RestaurantCreateRequest, db: Session = Depends(get_db)):
    db_restaurant = RestaurantService().create(db, restaurant)
    return db_restaurant

@router.post("/create", response_model=RestaurantResponse)
def create_restaurant(restaurant: RestaurantCreateRequest, db: Session = Depends(get_db)):
    db_restaurant = Restaurant(name=restaurant.name)
    db.add(db_restaurant)
    db.commit()
    db.refresh(db_restaurant)

    return RestaurantResponse(
        status=True,
        message="Restaurant created successfully",
        data=RestaurantRead.from_orm(db_restaurant)
    )


@router.get("/list", response_model=RestaurantListResponse)
def get_restaurants(db: Session = Depends(get_db)):
    restaurants = RestaurantService().get_all(db)

    return RestaurantListResponse(
        status=True,
        message="Restaurant list fetched",
        data=[RestaurantRead.from_orm(r) for r in restaurants]
    )


@router.get("/get/{restaurant_id}", response_model=GenericResponse)
def get_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    db_restaurant = RestaurantService().get_by_id(db, restaurant_id)

    if not db_restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    return GenericResponse(
        status=True,
        message="Restaurant fetched successfully",
        data=RestaurantRead.from_orm(db_restaurant)
    )
@router.delete("/delete/{restaurant_id}", response_model=GenericResponse)
def delete_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    if not RestaurantService().delete_by_id(db, restaurant_id):
        raise HTTPException(status_code=404, detail="Restaurant not found")

    return GenericResponse(
        status=True,
        message="Restaurant deleted successfully",
        data=None
    )