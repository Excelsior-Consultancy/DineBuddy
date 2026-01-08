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
    prefix="/menu-items",
    tags=["Menu Items"],
)

# ------------------------------------------------------------------
# CREATE MENU ITEM
# ------------------------------------------------------------------
@router.post("/", response_model=MenuItemRead)
def create_menu_item(
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

    # GLOBAL ITEM → ADMIN ONLY
    if data.is_global:
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin can create global menu items",
            )
        data.restaurant_id = None

    # RESTAURANT ITEM
    else:
        if not data.restaurant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="restaurant_id is required for restaurant menu items",
            )

        check_restaurant_access(
            restaurant_id=data.restaurant_id,
            current_user=current_user,
            db=db,
        )

    return menu_items_service.create_menu_item(db, data)


# ------------------------------------------------------------------
# GET MENU ITEM BY ID (PUBLIC)
# ------------------------------------------------------------------
@router.get("/{item_id}", response_model=MenuItemRead)
def get_menu_item(
    item_id: int,
    db: Session = Depends(get_db),
):
    item = menu_items_service.get_menu_item(db, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )
    return item


# ------------------------------------------------------------------
# LIST MENU ITEMS (PUBLIC)
# ------------------------------------------------------------------
@router.get("/", response_model=list[MenuItemRead])
def list_menu_items(
    restaurant_id: int | None = None,
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
# UPDATE MENU ITEM
# ------------------------------------------------------------------
@router.patch("/{item_id}", response_model=MenuItemRead)
def update_menu_item(
    item_id: int,
    data: MenuItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = menu_items_service.get_menu_item(db, item_id)
    if not item:
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

    # GLOBAL ITEM → ADMIN ONLY
    if item.is_global:
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin can update global menu items",
            )

    # RESTAURANT ITEM → ACCESS CHECK
    else:
        check_restaurant_access(
            restaurant_id=item.restaurant_id,
            current_user=current_user,
            db=db,
        )

    return menu_items_service.update_menu_item(db, item, data)


# ------------------------------------------------------------------
# DELETE MENU ITEM
# ------------------------------------------------------------------
@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = menu_items_service.get_menu_item(db, item_id)
    if not item:
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

    # GLOBAL ITEM → ADMIN ONLY
    if item.is_global:
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin can delete global menu items",
            )

    # RESTAURANT ITEM → ACCESS CHECK
    else:
        check_restaurant_access(
            restaurant_id=item.restaurant_id,
            current_user=current_user,
            db=db,
        )

    menu_items_service.delete_menu_item(db, item)
