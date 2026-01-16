from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.core.dependencies import (
    get_current_user,
    check_restaurant_access,
    require_admin,
)
from app.core.database import get_db
from app.services.restaurant_service import RestaurantService
from app.schemas.restaurant import (RestaurantCreateRequest, RestaurantUpdateRequest, RestaurantRead, RestaurantResponse, RestaurantListResponse, RestaurantDetailResponse, RestaurantProfileUpdateRequest, RestaurantStaffAddRequest)
from app.core.dependencies import get_accessible_restaurant_ids
from app.services.restaurant_setting_service import RestaurantSettingsService
from app.schemas.restaurant_setting_schema import RestaurantSettingsRead,RestaurantSettingsUpdateRequest
router = APIRouter(prefix="/restaurants", tags=["restaurants"])
service = RestaurantService()
settings_service = RestaurantSettingsService()


@router.post("/",response_model=RestaurantResponse,status_code=status.HTTP_201_CREATED)
def create_restaurant(
    payload: RestaurantCreateRequest,
    user: User = Depends(require_admin),  # Admin only
    db: Session = Depends(get_db),
):
    restaurant = service.create(db, payload)
    return RestaurantResponse(
        status=True,
        message="Restaurant created successfully",
        data=RestaurantRead.model_validate(restaurant),
    )


@router.get("/", response_model=RestaurantListResponse)
def get_restaurants(
    user: User = Depends(get_current_user),  # Use actual dependency
    db: Session = Depends(get_db),
    accessible_restaurant_ids: list[int] | None = Depends(get_accessible_restaurant_ids),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    skip = (page - 1) * limit

    restaurants, total = service.get_all(
        db=db,
        user=user,
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
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # ADMIN can access all; others must be assigned
    if user.role != UserRole.ADMIN:
        check_restaurant_access(restaurant_id, user, db)

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
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Only ADMIN or RESTAURANT_ADMIN
    if user.role not in [UserRole.ADMIN, UserRole.RESTAURANT_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Restaurant Admin access required",
        )
    # ADMIN can update any; RESTAURANT_ADMIN must be assigned
    if user.role != UserRole.ADMIN:
        check_restaurant_access(restaurant_id, user, db)

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


@router.patch("/{restaurant_id}/profile", response_model=RestaurantDetailResponse)
def update_restaurant_profile(
    restaurant_id: int,
    payload: RestaurantProfileUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Only ADMIN or RESTAURANT_ADMIN
    if user.role not in [UserRole.ADMIN, UserRole.RESTAURANT_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Restaurant Admin access required",
        )
    # ADMIN can update any; RESTAURANT_ADMIN must be assigned
    if user.role != UserRole.ADMIN:
        check_restaurant_access(restaurant_id, user, db)

    restaurant = service.update(db, restaurant_id, payload)

    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found",
        )

    return RestaurantDetailResponse(
        status=True,
        message="Restaurant profile updated successfully",
        data=RestaurantRead.model_validate(restaurant),
    )



@router.delete("/{restaurant_id}", response_model=RestaurantDetailResponse)
def delete_restaurant(
    restaurant_id: int,
    user: User = Depends(require_admin),  # Admin only
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


@router.post("/{restaurant_id}/staff", response_model=RestaurantDetailResponse)
def add_restaurant_staff(
    restaurant_id: int,
    payload: RestaurantStaffAddRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Add a staff user to a restaurant.
    - ADMIN can assign staff to any restaurant
    - RESTAURANT_ADMIN can assign staff only to their own restaurants
    """
    # Only ADMIN or RESTAURANT_ADMIN
    if user.role not in [UserRole.ADMIN, UserRole.RESTAURANT_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Restaurant Admin access required",
        )
    if user.role != UserRole.ADMIN:
        check_restaurant_access(restaurant_id, user, db)

    restaurant = service.add_staff(
        db=db,
        restaurant_id=restaurant_id,
        staff_user_id=payload.user_id,
    )

    return RestaurantDetailResponse(
        status=True,
        message="Staff assigned to restaurant",
        data=RestaurantRead.model_validate(restaurant),
    )

@router.get(
    "/{restaurant_id}/settings",
    response_model=RestaurantSettingsRead,
)
def get_restaurant_settings(
    restaurant_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.role not in [UserRole.ADMIN, UserRole.RESTAURANT_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Restaurant Admin access required",
        )

    if user.role != UserRole.ADMIN:
        check_restaurant_access(restaurant_id, user, db)

    settings = settings_service.get_or_create(db, restaurant_id)
    return RestaurantSettingsRead.model_validate(settings)
    
@router.patch(
    "/{restaurant_id}/settings",
    response_model=RestaurantSettingsUpdateRequest,
)
def update_restaurant_settings(
    restaurant_id: int,
    payload: RestaurantSettingsUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.role not in [UserRole.ADMIN, UserRole.RESTAURANT_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Restaurant Admin access required",
        )

    if user.role != UserRole.ADMIN:
        check_restaurant_access(restaurant_id, user, db)

    settings = settings_service.update(db, restaurant_id, payload)
    return RestaurantSettingsRead.model_validate(settings)

