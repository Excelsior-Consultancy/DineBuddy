from sqlalchemy.orm import Session
from app.models.menu_items import MenuItem
from app.schemas.menu_items_schema import MenuItemCreate, MenuItemUpdate


# ------------------------------------------------
# CREATE
# ------------------------------------------------
def create_menu_item(db: Session, data: MenuItemCreate) -> MenuItem:
    item = MenuItem(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


# ------------------------------------------------
# GET BY ID
# ------------------------------------------------
def get_menu_item(db: Session, item_id: int) -> MenuItem | None:
    return db.query(MenuItem).filter(MenuItem.id == item_id).first()


# ------------------------------------------------
# LIST (Restaurant Scoped)
# ------------------------------------------------
def list_menu_items(
    db: Session,
    restaurant_id: int,
    category_id: int | None = None,
):
    query = db.query(MenuItem).filter(
        MenuItem.restaurant_id == restaurant_id
    )

    if category_id:
        query = query.filter(MenuItem.category_id == category_id)

    return query.order_by(MenuItem.name.asc()).all()


# ------------------------------------------------
# UPDATE
# ------------------------------------------------
def update_menu_item(
    db: Session,
    item: MenuItem,
    data: MenuItemUpdate,
) -> MenuItem:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item


# ------------------------------------------------
# DELETE
# ------------------------------------------------
def delete_menu_item(db: Session, item: MenuItem) -> None:
    db.delete(item)
    db.commit()

# ------------------------------------------------
# Quick availability toggle
# ------------------------------------------------

def update_menu_item_availability(
    db: Session,
    item: MenuItem,
    is_available: bool
) -> MenuItem:
    item.is_available = is_available
    db.commit()
    db.refresh(item)
    return item
