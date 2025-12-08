# app/services/menucategory_service.py
from sqlalchemy.orm import Session
from app.models.menucategory import MenuCategory
from app.schemas.menucategoryschema import MenuCategoryCreate

class MenuCategoryService:
    """
    Service for MenuCategory model - provides instance methods for creation and retrieval of menu categories.
    """
    def create(self, db: Session, menu_category_create: MenuCategoryCreate) -> MenuCategory:
        menu_category = MenuCategory(
            name=menu_category_create.name,
            restaurant_id=menu_category_create.restaurant_id,
        )
        db.add(menu_category)
        db.commit()
        db.refresh(menu_category)
        return menu_category

    def get_by_id(self, db: Session, menu_category_id: int) -> MenuCategory:
        return db.query(MenuCategory).filter(MenuCategory.id == menu_category_id).first()

    def get_all(self, db: Session):
        return db.query(MenuCategory).all()
    
    def get_by_restaurant_id(self, db: Session, restaurant_id: int):
        """Get all categories for a specific restaurant"""
        return db.query(MenuCategory).filter(MenuCategory.restaurant_id == restaurant_id).all()