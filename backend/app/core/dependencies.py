from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.user_restaurant_map import UserRestaurant


def get_current_user(db: Session = Depends(get_db)) -> User:
    """
    Dummy current_user dependency.
    For production, replace this with your real authentication logic
    (e.g., extract user from JWT or session, check headers, etc.).
    """
    # Example: Always return the first user (replace logic for real auth!)
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized: No users in the system.")
    return user

def get_accessible_restaurant_ids(
    current_user: User,
    db: Session = Depends(get_db),
) -> list[int] | None:
    """
    - Admin → None (means no restriction)
    - Staff → list of restaurant_ids they belong to
    """

    if current_user.role == UserRole.ADMIN:
        return None  # No filtering

    restaurant_ids = (
        db.query(UserRestaurant.restaurant_id)
        .filter(UserRestaurant.user_id == current_user.id)
        .all()
    )

    ids = [r[0] for r in restaurant_ids]

    if not ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not assigned to any restaurant",
        )

    return ids
