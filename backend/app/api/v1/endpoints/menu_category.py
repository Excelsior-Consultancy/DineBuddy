from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.dependencies import (
    get_current_user,
    check_restaurant_access,
    require_admin,
)
from app.models.user import User
from app.schemas.menu_category_schema import (
    MenuCategoryCreate,
    MenuCategoryRead,
    MenuCategoryUpdate,
)
from app.services import menu_category_service

router = APIRouter(
    prefix="/restaurants/{restaurant_id}/menu-categories",
    tags=["Menu Categories"],
)


@router.post(
    "/",
    response_model=MenuCategoryRead,
    status_code=status.HTTP_201_CREATED,
)
def create_menu_category(
    restaurant_id: int,
    payload: MenuCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    ADMIN:
      - Can create global categories
      - Can create restaurant categories

    RESTAURANT_ADMIN:
      - Can create categories only for assigned restaurants
      - Cannot create global categories
    """

    if payload.is_global:
        # Admin-only global category
        require_admin(current_user)
        target_restaurant_id = None
    else:
        # Restaurant category
        check_restaurant_access(restaurant_id, current_user, db)
        target_restaurant_id = restaurant_id

    return menu_category_service.create_category(
        db=db,
        restaurant_id=target_restaurant_id,
        data=payload,
        user=current_user,
    )


@router.get(
    "/",
    response_model=List[MenuCategoryRead],
)
def list_menu_categories(
    restaurant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    ADMIN / RESTAURANT_ADMIN:
      - See restaurant categories
      - See global categories
    """

    check_restaurant_access(restaurant_id, current_user, db)

    return menu_category_service.list_categories(
        db=db,
        restaurant_id=restaurant_id,
    )


@router.patch(
    "/{category_id}",
    response_model=MenuCategoryRead,
)
def update_menu_category(
    restaurant_id: int,
    category_id: int,
    payload: MenuCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    ADMIN:
      - Can update any category

    RESTAURANT_ADMIN:
      - Can update only their restaurant categories
      - Cannot update global categories
    """

    return menu_category_service.update_category(
        db=db,
        category_id=category_id,
        data=payload,
        user=current_user,
    )


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_menu_category(
    restaurant_id: int,
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    ADMIN:
      - Can delete any category

    RESTAURANT_ADMIN:
      - Can delete only their restaurant categories
      - Cannot delete global categories
    """

    menu_category_service.delete_category(
        db=db,
        category_id=category_id,
        user=current_user,
    )
