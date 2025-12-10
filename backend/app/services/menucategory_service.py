from sqlalchemy.orm import Session
from app.models.menucategory import MenuCategory
from app.schemas.menucategoryschema import MenuCategoryCreateRequest


class MenuCategoryService:

    def create(self, db: Session, menu_category_data: MenuCategoryCreateRequest) -> MenuCategory:
        category = MenuCategory(
            name=menu_category_data.name,
            restaurant_id=menu_category_data.restaurant_id,
        )
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    def get_by_id(self, db: Session, category_id: int) -> MenuCategory:
        return db.query(MenuCategory).filter(MenuCategory.id == category_id).first()

    def get_all(self, db: Session):
        return db.query(MenuCategory).all()

    def delete(self, db: Session, category_id: int) -> bool:
        category = self.get_by_id(db, category_id)
        if not category:
            return False

        db.delete(category)
        db.commit()
        return True
