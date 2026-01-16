from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.user import User
from app.models.user_restaurant_map import UserRestaurant


# =========================================================
# Current User (Temporary Auth)
# =========================================================

def get_current_user(
    x_user_id: Optional[int] = Header(default=None, alias="X-User-Id"),
    db: Session = Depends(get_db),
) -> User:
    """
    Temporary auth dependency for development/testing.

    Reads user id from `X-User-Id` header and fetches user from DB.
    Replace with real JWT/session auth in production.
    """

    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-User-Id header is required",
        )

    user = db.query(User).filter(User.id == x_user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user",
        )

    return user


# =========================================================
# Restaurant Access Helpers
# =========================================================

def get_accessible_restaurant_ids(
    current_user: User,
    db: Session = Depends(get_db),
) -> Optional[List[int]]:
    """
    - ADMIN → None (no restriction)
    - RESTAURANT_ADMIN / STAFF → list of restaurant IDs they belong to
    """

    if current_user.is_admin:
        return None

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


def check_restaurant_access(
    restaurant_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """
    - ADMIN → full access
    - Others → must be assigned to the restaurant
    """

    if current_user.is_admin:
        return

    has_access = (
        db.query(UserRestaurant)
        .filter(
            UserRestaurant.user_id == current_user.id,
            UserRestaurant.restaurant_id == restaurant_id,
        )
        .first()
    )

    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this restaurant",
        )


# =========================================================
# Role Guards
# =========================================================

def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Require platform admin role."""

    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return current_user


def require_restaurant_admin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[int]:
    """
    Require restaurant admin role.
    Returns list of restaurant IDs assigned to the admin.
    """

    if not current_user.is_restaurant_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Restaurant admin access required",
        )

    restaurant_ids = (
        db.query(UserRestaurant.restaurant_id)
        .filter(UserRestaurant.user_id == current_user.id)
        .all()
    )

    ids = [r[0] for r in restaurant_ids]

    if not ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Restaurant admin is not assigned to any restaurant",
        )

    return ids
