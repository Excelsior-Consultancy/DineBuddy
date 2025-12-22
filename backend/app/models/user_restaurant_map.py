from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from app.db.base import Base, TimestampMixin


class UserRestaurant(Base, TimestampMixin):
<<<<<<< HEAD:backend/app/models/junction_table.py
    __tablename__ = "user_junction"
=======
    __tablename__ = "user_restaurants_map"
>>>>>>> excel-67-Add-restaurant-id-to-User-model:backend/app/models/user_restaurant_map.py

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )

    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("user_id", "restaurant_id", name="uq_user_restaurant"),
    )
