from sqlalchemy.orm import Session
from app.models.menu_items import MenuItem
from app.schemas.menu_items_schema import MenuItemCreate, MenuItemUpdate


def create_menu_item(db: Session, data: MenuItemCreate) -> MenuItem:
    item = MenuItem(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_menu_item(db: Session, item_id: int) -> MenuItem | None:
    return db.query(MenuItem).filter(MenuItem.id == item_id).first()


def list_menu_items(
    db: Session,
    restaurant_id: int | None = None,
    category_id: int | None = None,
    include_global: bool = True,
):
    query = db.query(MenuItem)

    if category_id:
        query = query.filter(MenuItem.category_id == category_id)

    if restaurant_id is not None:
        if include_global:
            query = query.filter(
                (MenuItem.restaurant_id == restaurant_id)
                | (MenuItem.is_global.is_(True))
            )
        else:
            query = query.filter(MenuItem.restaurant_id == restaurant_id)

    return query.order_by(MenuItem.name.asc()).all()


def update_menu_item(
    db: Session, item: MenuItem, data: MenuItemUpdate
) -> MenuItem:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item


def delete_menu_item(db: Session, item: MenuItem):
    db.delete(item)
    db.commit()
