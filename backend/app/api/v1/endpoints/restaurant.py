from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.restaurant_service import RestaurantService
from app.schemas.restaurant import (RestaurantCreateRequest, RestaurantUpdateRequest, RestaurantRead, RestaurantResponse, RestaurantListResponse, RestaurantDetailResponse)
from app.core.dependencies import get_accessible_restaurant_ids, get_current_user
from app.models.user import User

router = APIRouter(prefix="/restaurants", tags=["restaurants"])
service = RestaurantService()



@router.post("/",response_model=RestaurantResponse,status_code=status.HTTP_201_CREATED)
def create_restaurant(payload: RestaurantCreateRequest,db: Session = Depends(get_db)):
    restaurant = service.create(db, payload)
    return RestaurantResponse(
        status=True,
        message="Restaurant created successfully",
        data=RestaurantRead.model_validate(restaurant),
    )


@router.get("/", response_model=RestaurantListResponse)
def get_restaurants(
    db: Session = Depends(get_db),
    accessible_restaurant_ids: list[int] | None = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    skip = (page - 1) * limit

    restaurants, total = service.get_all(
        db=db,
        accessible_restaurant_ids=accessible_restaurant_ids,
        skip=skip,
        limit=limit,
    )

    return RestaurantListResponse(
        status=True,
        message="Restaurant list fetched",
        data=[RestaurantRead.model_validate(r) for r in restaurants],
        meta={"page": page, "limit": limit, "total": total},
    )



@router.get("/{restaurant_id}", response_model=RestaurantDetailResponse)
def get_restaurant(
    restaurant_id: int,
    db: Session = Depends(get_db),
):
    restaurant = service.get_by_id(db, restaurant_id)

    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found",
        )

    return RestaurantDetailResponse(
        status=True,
        message="Restaurant fetched successfully",
        data=RestaurantRead.model_validate(restaurant),
    )

@router.patch("/{restaurant_id}", response_model=RestaurantDetailResponse)
def update_restaurant(
    restaurant_id: int,
    payload: RestaurantUpdateRequest,
    db: Session = Depends(get_db),
):
    restaurant = service.update(db, restaurant_id, payload)

    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found",
        )

    return RestaurantDetailResponse(
        status=True,
        message="Restaurant updated successfully",
        data=RestaurantRead.model_validate(restaurant),
    )




@router.delete("/{restaurant_id}", response_model=RestaurantDetailResponse)
def delete_restaurant(
    restaurant_id: int,
    db: Session = Depends(get_db),
):
    deleted = service.delete(db, restaurant_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found",
        )

    return RestaurantDetailResponse(
        status=True,
        message="Restaurant deleted successfully",
        data=None,
    )
