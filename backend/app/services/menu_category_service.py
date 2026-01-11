from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.menu_category import MenuCategory
from app.models.user import User, UserRole
from app.core.dependencies import check_restaurant_access


def create_category(
    db: Session,
    restaurant_id: int | None,
    data,
    user: User,
):
    # Only platform admin can create global categories
    if getattr(data, "is_global", False):
        if user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin can create global categories"
            )
        restaurant_id = None
    else:
        # Restaurant category → validate access
        check_restaurant_access(restaurant_id, user, db)

    category = MenuCategory(
        restaurant_id=restaurant_id,
        **data.model_dump(),
    )

    try:
        db.add(category)
        db.commit()
        db.refresh(category)
        return category
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
        )


def list_categories(
    db: Session,
    restaurant_id: int | None,
):
    query = db.query(MenuCategory).filter(MenuCategory.is_active.is_(True))

    if restaurant_id:
        query = query.filter(
            (MenuCategory.restaurant_id == restaurant_id)
            | (MenuCategory.is_global.is_(True))
        )
    else:
        query = query.filter(MenuCategory.is_global.is_(True))

    return query.order_by(MenuCategory.display_order).all()


def get_category(
    db: Session,
    category_id: int,
    user: User,
):
    category = db.query(MenuCategory).filter(
        MenuCategory.id == category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu category not found"
        )

    # Access control for restaurant categories
    if not category.is_global:
        check_restaurant_access(category.restaurant_id, user, db)

    return category


def update_category(
    db: Session,
    category_id: int,
    data,
    user: User,
):
    category = get_category(db, category_id, user)

    if category.is_global and user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can update global categories"
        )

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(category, field, value)

    try:
        db.commit()
        db.refresh(category)
        return category
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
        )


def delete_category(
    db: Session,
    category_id: int,
    user: User,
):
    category = get_category(db, category_id, user)

    if category.is_global and user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can delete global categories"
        )

    category.is_active = False
    db.commit()
