from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.user_restaurant_map import UserRestaurant


# def get_current_user(db: Session = Depends(get_db)) -> User:
#     """
#     Dummy current_user dependency.
#     For production, replace this with your real authentication logic
#     (e.g., extract user from JWT or session, check headers, etc.).
#     """
#     # Example: Always return the first user (replace logic for real auth!)
#     user = db.query(User).first()
#     if not user:
#         raise HTTPException(status_code=401, detail="Unauthorized: No users in the system.")
#     return user


def get_current_user(
    x_user_id: int | None = Header(default=None, alias="X-User-Id"),
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

def check_restaurant_access(
    restaurant_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """
    - ADMIN: full access
    - Others: must be assigned to the restaurant
    """
    if current_user.role == UserRole.ADMIN:
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


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require platform admin role."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


def require_restaurant_admin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[int]:

    if current_user.role != UserRole.RESTAURANT_ADMIN:
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
