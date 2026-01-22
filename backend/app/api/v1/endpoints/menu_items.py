from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.permission import require_roles
from app.core.database import get_db
from app.core.dependencies import CurrentUser, get_current_user, check_restaurant_access
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
    db: Session = Depends(get_db),
):
    return menu_items_service.list_menu_items(
        db,
        restaurant_id=restaurant_id,
        category_id=category_id,
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

    if not item or item.restaurant_id != restaurant_id:
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
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    
):
    require_roles(
        current_user,
        (UserRole.ADMIN, UserRole.RESTAURANT_ADMIN),
    )

    check_restaurant_access(restaurant_id, current_user, db)
    data.restaurant_id = restaurant_id

    return menu_items_service.create_menu_item(db, data)

# ------------------------------------------------------------------
# UPDATE MENU ITEM
# ------------------------------------------------------------------
@router.patch("/{item_id}", response_model=MenuItemRead)
def update_menu_item(
    restaurant_id: int,
    item_id: int,
    data: MenuItemUpdate,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    item = menu_items_service.get_menu_item(db, item_id)
    if not item or item.restaurant_id != restaurant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")

    require_roles(current_user, (UserRole.ADMIN, UserRole.RESTAURANT_ADMIN))
    check_restaurant_access(restaurant_id, current_user, db)

    return menu_items_service.update_menu_item(db, item, data)


# DELETE MENU ITEM
@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu_item(
    restaurant_id: int,
    item_id: int,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    
):
    item = menu_items_service.get_menu_item(db, item_id)
    if not item or item.restaurant_id != restaurant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")

    require_roles(current_user, (UserRole.ADMIN, UserRole.RESTAURANT_ADMIN))
    check_restaurant_access(restaurant_id, current_user, db)

    menu_items_service.delete_menu_item(db, item)