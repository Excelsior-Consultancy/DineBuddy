from sqlalchemy.orm import Session
from app.models.restaurant import Restaurant
from app.schemas.restaurant import RestaurantCreate

class RestaurantService:
<<<<<<< HEAD
    """
    Service for Restaurant model - provides instance methods for creation and retrieval of restaurants.
    """
    def create(self, db: Session, restaurant_create: RestaurantCreate) -> Restaurant:
        restaurant = Restaurant(name=restaurant_create.name)
=======

    def create(self, db: Session, name: str):
        restaurant = Restaurant(name=name)
>>>>>>> excel-28-create-restaurant
        db.add(restaurant)
        db.commit()
        db.refresh(restaurant)
        return restaurant

    def get_all(self, db: Session):
        return db.query(Restaurant).all()

    def get_by_id(self, db: Session, restaurant_id: int):
        return db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()

    def delete_by_id(self, db: Session, restaurant_id: int):
        restaurant = self.get_by_id(db, restaurant_id)
        if not restaurant:
            return False
        db.delete(restaurant)
        db.commit()
        return True
