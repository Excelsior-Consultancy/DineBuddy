from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user, check_restaurant_access
from app.models.user import User, UserRole
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


@router.post("/", response_model=MenuCategoryRead, status_code=status.HTTP_201_CREATED)
def create_menu_category(
    restaurant_id: int,
    payload: MenuCategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    ADMIN:
      - Can create global categories
      - Can create restaurant categories

    RESTAURANT_ADMIN:
      - Can create categories for assigned restaurants
      - Cannot create global categories
    """

    # Global category → ADMIN only
    if payload.is_global:
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only platform admins can create global categories",
            )
        target_restaurant_id = None
    else:
        # Restaurant category
        check_restaurant_access(restaurant_id, current_user, db)
        target_restaurant_id = restaurant_id

    return menu_category_service.create_category(
        db=db,
        restaurant_id=target_restaurant_id,
        data=payload,
    )


@router.get("/", response_model=List[MenuCategoryRead])
def list_menu_categories(
    restaurant_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
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


@router.patch("/{category_id}", response_model=MenuCategoryRead)
def update_menu_category(
    restaurant_id: int,
    category_id: int,
    payload: MenuCategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    ADMIN:
      - Can update any category

    RESTAURANT_ADMIN:
      - Can update only their restaurant categories
      - Cannot update global categories
    """

    category = menu_category_service.get_category(db, category_id)

    if not category:
        raise HTTPException(status_code=404, detail="Menu category not found")

    # Global category protection
    if category.is_global and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only platform admins can update global categories",
        )

    # Restaurant category checks
    if not category.is_global:
        if category.restaurant_id != restaurant_id:
            raise HTTPException(status_code=404, detail="Menu category not found")

        check_restaurant_access(restaurant_id, current_user, db)

    return menu_category_service.update_category(
        db=db,
        category=category,
        data=payload,
    )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu_category(
    restaurant_id: int,
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    ADMIN:
      - Can delete any category

    RESTAURANT_ADMIN:
      - Can delete only their restaurant categories
      - Cannot delete global categories
    """

    category = menu_category_service.get_category(db, category_id)

    if not category:
        raise HTTPException(status_code=404, detail="Menu category not found")

    # Global category protection
    if category.is_global and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only platform admins can delete global categories",
        )

    # Restaurant category checks
    if not category.is_global:
        if category.restaurant_id != restaurant_id:
            raise HTTPException(status_code=404, detail="Menu category not found")

        check_restaurant_access(restaurant_id, current_user, db)

    menu_category_service.delete_category(db, category)
