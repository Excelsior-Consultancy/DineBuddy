from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.restaurant_service import RestaurantService
from app.schemas.restaurant import RestaurantCreate, RestaurantRead
from typing import List
from app.core.database import get_db  # This should be your SQLAlchemy Session dependency

router = APIRouter(prefix="/restaurants", tags=["restaurants"])

# ------ Endpoints ------ #
@router.post("/create", response_model=RestaurantRead)
def create_restaurant(restaurant: RestaurantCreate, db: Session = Depends(get_db)):
    db_restaurant = RestaurantService().create(db, restaurant)
    return db_restaurant

@router.get("/list", response_model=List[RestaurantRead])
def get_restaurants(db: Session = Depends(get_db)):
    return RestaurantService().get_all(db)

@router.get("/get/{restaurant_id}", response_model=RestaurantRead)
def get_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    db_restaurant = RestaurantService().get_by_id(db, restaurant_id)
    if not db_restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return db_restaurant
