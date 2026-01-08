from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import (
    get_current_user,
    check_restaurant_access,
)
from app.models.user import User, UserRole
from app.schemas.menu_items_schema import (
    MenuItemCreate,
    MenuItemRead,
    MenuItemUpdate,
)
from app.services import menu_items_service


router = APIRouter(
    prefix="/restaurants/{restaurant_id}/menu-items",
    tags=["Restaurant Menu Items"],
)

# ------------------------------------------------------------------
# LIST MENU ITEMS (PUBLIC)
# ------------------------------------------------------------------
@router.get("/", response_model=list[MenuItemRead])
def list_menu_items(
    restaurant_id: int,
    category_id: int | None = None,
    include_global: bool = True,
    db: Session = Depends(get_db),
):
    return menu_items_service.list_menu_items(
        db,
        restaurant_id=restaurant_id,
        category_id=category_id,
        include_global=include_global,
    )


# ------------------------------------------------------------------
# GET MENU ITEM BY ID (PUBLIC)
# ------------------------------------------------------------------
@router.get("/{item_id}", response_model=MenuItemRead)
def get_menu_item(
    restaurant_id: int,
    item_id: int,
    db: Session = Depends(get_db),
):
    item = menu_items_service.get_menu_item(db, item_id)

    if not item or (
        not item.is_global and item.restaurant_id != restaurant_id
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )

    return item


# ------------------------------------------------------------------
# CREATE MENU ITEM
# ------------------------------------------------------------------
@router.post("/", response_model=MenuItemRead)
def create_menu_item(
    restaurant_id: int,
    data: MenuItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Only ADMIN or RESTAURANT_ADMIN
    if current_user.role not in (
        UserRole.ADMIN,
        UserRole.RESTAURANT_ADMIN,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to create menu items",
        )

    # Prevent global creation via restaurant route
    if data.is_global:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Global menu items cannot be created under a restaurant",
        )

    # Restaurant admin must have access
    check_restaurant_access(
        restaurant_id=restaurant_id,
        current_user=current_user,
        db=db,
    )

    data.restaurant_id = restaurant_id
    data.is_global = False

    return menu_items_service.create_menu_item(db, data)


# ------------------------------------------------------------------
# UPDATE MENU ITEM
# ------------------------------------------------------------------
@router.patch("/{item_id}", response_model=MenuItemRead)
def update_menu_item(
    restaurant_id: int,
    item_id: int,
    data: MenuItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = menu_items_service.get_menu_item(db, item_id)
    if not item or item.restaurant_id != restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )

    # Only ADMIN or RESTAURANT_ADMIN
    if current_user.role not in (
        UserRole.ADMIN,
        UserRole.RESTAURANT_ADMIN,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to update menu items",
        )

    # Global item safety (extra guard)
    if item.is_global:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Global menu items cannot be modified here",
        )

    check_restaurant_access(
        restaurant_id=restaurant_id,
        current_user=current_user,
        db=db,
    )

    # Prevent switching restaurant / global
    data_dict = data.model_dump(exclude_unset=True)
    data_dict.pop("is_global", None)
    data_dict.pop("restaurant_id", None)

    return menu_items_service.update_menu_item(
        db,
        item,
        MenuItemUpdate(**data_dict),
    )


# ------------------------------------------------------------------
# DELETE MENU ITEM
# ------------------------------------------------------------------
@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu_item(
    restaurant_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = menu_items_service.get_menu_item(db, item_id)
    if not item or item.restaurant_id != restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )

    # Only ADMIN or RESTAURANT_ADMIN
    if current_user.role not in (
        UserRole.ADMIN,
        UserRole.RESTAURANT_ADMIN,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to delete menu items",
        )

    # Global item safety
    if item.is_global:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Global menu items cannot be deleted here",
        )

    check_restaurant_access(
        restaurant_id=restaurant_id,
        current_user=current_user,
        db=db,
    )

    menu_items_service.delete_menu_item(db, item)
