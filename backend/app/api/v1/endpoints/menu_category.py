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
    # Restaurant access required only for non-global categories
    if not payload.is_global:
        check_restaurant_access(restaurant_id, current_user, db)

    return menu_category_service.create_category(
        db=db,
        restaurant_id=restaurant_id,
        data=payload,
        user=current_user,
    )


@router.get("/", response_model=List[MenuCategoryRead])
def list_menu_categories(
    restaurant_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
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
    return menu_category_service.update_category(
        db=db,
        category_id=category_id,
        data=payload,
        user=current_user,
    )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu_category(
    restaurant_id: int,
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    menu_category_service.delete_category(
        db=db,
        category_id=category_id,
        user=current_user,
    )
