# app/core/dependencies.py
from typing import List, Optional, Annotated
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.user_restaurant_map import UserRestaurant

# =========================================================
# Temporary "current user" dependency for testing
# =========================================================
def get_current_user(
    x_user_id: Optional[int] = Header(default=None, alias="X-User-Id"),
    db: Session = Depends(get_db),
) -> User:
    """
    Temporary auth dependency.

    Reads user id from `X-User-Id` header and fetches user from DB.
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
            detail="User not found",
        )
    return user

# =========================================================
# Role Guards
# =========================================================
def require_admin(current_user: User = Depends(get_current_user)) -> User:
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
            detail="No restaurants assigned",
        )

    return ids

# =========================================================
# Restaurant access
# =========================================================
def check_restaurant_access(
    restaurant_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
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
            detail="Access denied to this restaurant",
        )

# =========================================================
# Dependency aliases for clean routes
# =========================================================
DBSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(require_admin)]
RestaurantAdminRestaurantIds = Annotated[List[int], Depends(require_restaurant_admin)]
RestaurantAccess = Annotated[None, Depends(check_restaurant_access)]
