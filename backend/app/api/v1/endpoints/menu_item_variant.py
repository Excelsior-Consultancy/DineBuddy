from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, check_restaurant_access
from app.models.user import User, UserRole
from app.models.menu_items import MenuItem
from app.models.menu_item_variant import MenuItemVariant
from app.schemas.menu_item_variant_schema import (
    MenuItemVariantCreate,
    MenuItemVariantRead,
    MenuItemVariantUpdate,
)
from app.services import menu_item_variant_service


router = APIRouter(
    prefix="/restaurants/{restaurant_id}/menu-items/{item_id}/variants",
    tags=["Menu Item Variants"],
)

# ------------------------------------------------
# LIST VARIANTS (PUBLIC)
# ------------------------------------------------
@router.get("/", response_model=list[MenuItemVariantRead])
def list_variants(
    restaurant_id: int,
    item_id: int,
    db: Session = Depends(get_db),
):
    item = (
        db.query(MenuItem)
        .filter(
            MenuItem.id == item_id,
            MenuItem.restaurant_id == restaurant_id,
        )
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )

    return menu_item_variant_service.list_variants(db, item_id)


# ------------------------------------------------
# CREATE VARIANT
# ------------------------------------------------
@router.post("/", response_model=MenuItemVariantRead, status_code=status.HTTP_201_CREATED)
def create_variant(
    restaurant_id: int,
    item_id: int,
    data: MenuItemVariantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in (
        UserRole.ADMIN,
        UserRole.RESTAURANT_ADMIN,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to create variants",
        )

    item = (
        db.query(MenuItem)
        .filter(
            MenuItem.id == item_id,
            MenuItem.restaurant_id == restaurant_id,
        )
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )

    check_restaurant_access(
        restaurant_id=restaurant_id,
        current_user=current_user,
        db=db,
    )

    return menu_item_variant_service.create_variant(db, item_id, data)


# ------------------------------------------------
# UPDATE VARIANT
# ------------------------------------------------
@router.patch("/{variant_id}", response_model=MenuItemVariantRead)
def update_variant(
    restaurant_id: int,
    item_id: int,
    variant_id: int,
    data: MenuItemVariantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in (
        UserRole.ADMIN,
        UserRole.RESTAURANT_ADMIN,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to update variants",
        )

    variant = (
        db.query(MenuItemVariant)
        .filter(
            MenuItemVariant.id == variant_id,
            MenuItemVariant.item_id == item_id,
        )
        .first()
    )

    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Variant not found",
        )

    item = (
        db.query(MenuItem)
        .filter(
            MenuItem.id == item_id,
            MenuItem.restaurant_id == restaurant_id,
        )
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )

    check_restaurant_access(
        restaurant_id=restaurant_id,
        current_user=current_user,
        db=db,
    )

    return menu_item_variant_service.update_variant(db, variant, data)


# ------------------------------------------------
# DELETE VARIANT
# ------------------------------------------------
@router.delete("/{variant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_variant(
    restaurant_id: int,
    item_id: int,
    variant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in (
        UserRole.ADMIN,
        UserRole.RESTAURANT_ADMIN,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to delete variants",
        )

    variant = (
        db.query(MenuItemVariant)
        .filter(
            MenuItemVariant.id == variant_id,
            MenuItemVariant.item_id == item_id,
        )
        .first()
    )

    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Variant not found",
        )

    item = (
        db.query(MenuItem)
        .filter(
            MenuItem.id == item_id,
            MenuItem.restaurant_id == restaurant_id,
        )
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )

    check_restaurant_access(
        restaurant_id=restaurant_id,
        current_user=current_user,
        db=db,
    )

    menu_item_variant_service.delete_variant(db, variant)
