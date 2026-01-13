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
# LIST (Public)
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
        raise HTTPException(status_code=404, detail="Menu item not found")

    return menu_item_variant_service.list_variants(db, item_id)


# ------------------------------------------------
# CREATE
# ------------------------------------------------
@router.post("/", response_model=MenuItemVariantRead, status_code=201)
def create_variant(
    restaurant_id: int,
    item_id: int,
    data: MenuItemVariantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in (UserRole.ADMIN, UserRole.RESTAURANT_ADMIN):
        raise HTTPException(status_code=403, detail="Not allowed")

    item = (
        db.query(MenuItem)
        .filter(
            MenuItem.id == item_id,
            MenuItem.restaurant_id == restaurant_id,
        )
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    if item.is_global and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Cannot modify global menu item",
        )

    if not item.is_global:
        check_restaurant_access(item.restaurant_id, current_user, db)

    return menu_item_variant_service.create_variant(db, item_id, data)


# ------------------------------------------------
# UPDATE
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
    if current_user.role not in (UserRole.ADMIN, UserRole.RESTAURANT_ADMIN):
        raise HTTPException(status_code=403, detail="Not allowed")

    variant = (
        db.query(MenuItemVariant)
        .filter(
            MenuItemVariant.id == variant_id,
            MenuItemVariant.item_id == item_id,
        )
        .first()
    )

    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")

    item = (
        db.query(MenuItem)
        .filter(
            MenuItem.id == item_id,
            MenuItem.restaurant_id == restaurant_id,
        )
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    if item.is_global and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Cannot modify global menu item")

    if not item.is_global:
        check_restaurant_access(item.restaurant_id, current_user, db)

    return menu_item_variant_service.update_variant(db, variant, data)


# ------------------------------------------------
# DELETE
# ------------------------------------------------
@router.delete("/{variant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_variant(
    restaurant_id: int,
    item_id: int,
    variant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in (UserRole.ADMIN, UserRole.RESTAURANT_ADMIN):
        raise HTTPException(status_code=403, detail="Not allowed")

    variant = (
        db.query(MenuItemVariant)
        .filter(
            MenuItemVariant.id == variant_id,
            MenuItemVariant.item_id == item_id,
        )
        .first()
    )

    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")

    item = (
        db.query(MenuItem)
        .filter(
            MenuItem.id == item_id,
            MenuItem.restaurant_id == restaurant_id,
        )
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    if item.is_global and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Cannot modify global menu item")

    if not item.is_global:
        check_restaurant_access(item.restaurant_id, current_user, db)

    menu_item_variant_service.delete_variant(db, variant)
    return None
