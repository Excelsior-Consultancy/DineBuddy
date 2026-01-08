from sqlalchemy.orm import Session
from app.models.menu_category import MenuCategory


def create_category(db: Session, restaurant_id: int | None, data):
    category = MenuCategory(
        restaurant_id=restaurant_id,
        **data.model_dump(),
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def list_categories(db: Session, restaurant_id: int | None):
    query = db.query(MenuCategory).filter(MenuCategory.is_active.is_(True))

    if restaurant_id:
        query = query.filter(
            (MenuCategory.restaurant_id == restaurant_id)
            | (MenuCategory.is_global.is_(True))
        )

    return query.order_by(MenuCategory.display_order).all()
