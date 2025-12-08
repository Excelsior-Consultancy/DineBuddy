from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.menuitem import MenuItemCreate, MenuItemRead
from app.services.menuitem_service import MenuItemService

router = APIRouter(prefix="/menuitem", tags=["menuitem"])


@router.post("/create", response_model=MenuItemRead)
def create_menu_item(
    menu_item: MenuItemCreate,
    db: Session = Depends(get_db)
):
    """Create a new menu item in a category"""
    try:
        db_item = MenuItemService().create(db, menu_item)
        return db_item
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating menu item: {str(e)}")


@router.get("/list", response_model=List[MenuItemRead])
def list_menu_items(db: Session = Depends(get_db)):
    """Get all menu items"""
    return MenuItemService().get_all(db)


@router.get("/get/{menu_item_id}", response_model=MenuItemRead)
def get_menu_item(menu_item_id: int, db: Session = Depends(get_db)):
    """Get a specific menu item by ID"""
    db_item = MenuItemService().get_by_id(db, menu_item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return db_item


@router.get("/category/{menu_category_id}", response_model=List[MenuItemRead])
def get_menu_items_by_category(menu_category_id: int, db: Session = Depends(get_db)):
    """Get all menu items in a specific category"""
    items = MenuItemService().get_by_category_id(db, menu_category_id)
    return items


@router.get("/restaurant/{restaurant_id}", response_model=List[MenuItemRead])
def get_menu_items_by_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    """Get all menu items for a specific restaurant (across all categories)"""
    items = MenuItemService().get_by_restaurant_id(db, restaurant_id)
    return items


@router.put("/update/{menu_item_id}", response_model=MenuItemRead)
def update_menu_item(
    menu_item_id: int,
    menu_item: MenuItemCreate,
    db: Session = Depends(get_db)
):
    """Update a menu item"""
    try:
        db_item = MenuItemService().update(db, menu_item_id, menu_item)
        if not db_item:
            raise HTTPException(status_code=404, detail="Menu item not found")
        return db_item
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error updating menu item: {str(e)}")


@router.delete("/delete/{menu_item_id}", status_code=204)
def delete_menu_item(menu_item_id: int, db: Session = Depends(get_db)):
    """Delete a menu item"""
    success = MenuItemService().delete(db, menu_item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return None

