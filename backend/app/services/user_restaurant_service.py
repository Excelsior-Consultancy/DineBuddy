from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.user_restaurant_map import UserRestaurant


class UserRestaurantService:

    def assign_user_to_restaurant(
        self,
        db: Session,
        user_id: int,
        restaurant_id: int,
    ):
        mapping = UserRestaurant(
            user_id=user_id,
            restaurant_id=restaurant_id,
        )

        db.add(mapping)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already assigned to this restaurant",
            )

        return True
