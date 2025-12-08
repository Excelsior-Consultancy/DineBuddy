# app/services/menuitem_service.py
from sqlalchemy.orm import Session
from app.models.menuitem import MenuItem
from app.models.menucategory import MenuCategory
from app.schemas.menuitem import MenuItemCreate

class MenuItemService:
    """
    Service for MenuItem model - provides instance methods for creation and retrieval of menu items.
    """
    def create(self, db: Session, menu_item_create: MenuItemCreate) -> MenuItem:
        # Validate that the menu category exists
        category = db.query(MenuCategory).filter(MenuCategory.id == menu_item_create.menu_category_id).first()
        if not category:
            raise ValueError(f"Menu category with id {menu_item_create.menu_category_id} not found")
        
        menu_item = MenuItem(
            name=menu_item_create.name,
            description=menu_item_create.description,
            price=menu_item_create.price,
            menu_category_id=menu_item_create.menu_category_id,
        )
        db.add(menu_item)
        db.commit()
        db.refresh(menu_item)
        return menu_item

    def get_by_id(self, db: Session, menu_item_id: int) -> MenuItem:
        return db.query(MenuItem).filter(MenuItem.id == menu_item_id).first()

    def get_all(self, db: Session):
        return db.query(MenuItem).all()
    
    def get_by_category_id(self, db: Session, menu_category_id: int):
        """Get all menu items for a specific category"""
        return db.query(MenuItem).filter(MenuItem.menu_category_id == menu_category_id).all()
    
    def get_by_restaurant_id(self, db: Session, restaurant_id: int):
        """Get all menu items for a specific restaurant (through categories)"""
        from app.models.menucategory import MenuCategory
        return db.query(MenuItem).join(MenuCategory).filter(
            MenuCategory.restaurant_id == restaurant_id
        ).all()
    
    def update(self, db: Session, menu_item_id: int, menu_item_update: MenuItemCreate) -> MenuItem:
        menu_item = self.get_by_id(db, menu_item_id)
        if not menu_item:
            return None
        
        # Validate that the menu category exists
        category = db.query(MenuCategory).filter(MenuCategory.id == menu_item_update.menu_category_id).first()
        if not category:
            raise ValueError(f"Menu category with id {menu_item_update.menu_category_id} not found")
        
        menu_item.name = menu_item_update.name
        menu_item.description = menu_item_update.description
        menu_item.price = menu_item_update.price
        menu_item.menu_category_id = menu_item_update.menu_category_id
        
        db.commit()
        db.refresh(menu_item)
        return menu_item
    
    def delete(self, db: Session, menu_item_id: int) -> bool:
        menu_item = self.get_by_id(db, menu_item_id)
        if not menu_item:
            return False
        
        db.delete(menu_item)
        db.commit()
        return True

