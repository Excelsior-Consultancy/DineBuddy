from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.user import User
from app.models.restaurant import Restaurant
from app.utils.slug_generator import generate_unique_slug


class RestaurantService:

    def create(self, db: Session, payload):
        slug = generate_unique_slug(db, payload.name)

        restaurant = Restaurant(
            name=payload.name,
            slug=slug,
            address=payload.address,
            phone=payload.phone,
            email=payload.email,
            logo_url=payload.logo_url,
            timezone=payload.timezone,
            currency=payload.currency,
            is_active=True
        )

        db.add(restaurant)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Restaurant with this name or slug already exists"
            )

        db.refresh(restaurant)
        return restaurant

    def get_all(
        self,
        db: Session,
        accessible_restaurant_ids: list[int] | None,
        skip: int = 0,
        limit: int = 10,
    ):
        query = db.query(Restaurant)

        # 🔐 Apply restriction ONLY if staff
        if accessible_restaurant_ids is not None:
            query = query.filter(Restaurant.id.in_(accessible_restaurant_ids))

        total = query.count()

        restaurants = (
            query
            .order_by(Restaurant.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return restaurants, total


    def get_by_id(self, db: Session, restaurant_id: int):
        return (
            db.query(Restaurant)
            .filter(Restaurant.id == restaurant_id)
            .first()
        )

    def update(self, db: Session, restaurant_id: int, payload):
        restaurant = self.get_by_id(db, restaurant_id)
        if not restaurant:
            return None

        data = payload.dict(exclude_unset=True)

        # Regenerate slug only if name changes
        if "name" in data:
            restaurant.name = data["name"]
            restaurant.slug = generate_unique_slug(
                db,
                data["name"],
                exclude_id=restaurant.id
            )

        for key, value in data.items():
            if key != "name":
                setattr(restaurant, key, value)

        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Restaurant with this name or slug already exists"
            )

        db.refresh(restaurant)
        return restaurant

    def delete(self, db: Session, restaurant_id: int):
        restaurant = self.get_by_id(db, restaurant_id)
        if not restaurant:
            return False

        db.delete(restaurant)
        db.commit()
        return True
