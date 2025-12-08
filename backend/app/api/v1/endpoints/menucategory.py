from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.menucategoryschema import MenuCategoryCreate, MenuCategoryRead
from app.services.menucategory_service import MenuCategoryService

router = APIRouter(prefix="/menucategory", tags=["menucategory"])


@router.post("/create", response_model=MenuCategoryRead)
def create_menu_category(
    menu_category: MenuCategoryCreate,
    db: Session = Depends(get_db)
):
    db_category = MenuCategoryService().create(db, menu_category)
    return db_category


@router.get("/list", response_model=List[MenuCategoryRead])
def list_menu_categories(db: Session = Depends(get_db)):
    return MenuCategoryService().get_all(db)


@router.get("/get/{menu_category_id}", response_model=MenuCategoryRead)
def get_menu_category(menu_category_id: int, db: Session = Depends(get_db)):
    db_category = MenuCategoryService().get_by_id(db, menu_category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Menu category not found")
    return db_category


@router.get("/restaurant/{restaurant_id}", response_model=List[MenuCategoryRead])
def get_menu_categories_by_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    """Get all menu categories for a specific restaurant"""
    categories = MenuCategoryService().get_by_restaurant_id(db, restaurant_id)
    return categories
